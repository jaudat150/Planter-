import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array #type:ignore
from tensorflow.keras import layers, models, regularizers#type:ignore
from tensorflow.keras.applications import MobileNetV2#type:ignore
from tensorflow.keras.optimizers import Adam#type:ignore
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint#type:ignore
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import json


# ================== GPU Configuration ==================
print("Checking GPU availability...")
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # Use the first GPU
        tf.config.set_visible_devices(gpus[0], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print(f"Using GPU: {gpus[0]}")
    except RuntimeError as e:
        print(e)
else:
    print("No GPU found, running on CPU.")

# ================== Configuration ==================
# Paths
train_dir = 'C:\\Users\\jauda\\Desktop\\SemesterProject\\dataset\\train'
val_dir = 'C:\\Users\\jauda\\Desktop\\SemesterProject\\dataset\\validation'

# Hyperparameters
#this is the input size for the mobilnetv2
img_size = (224, 224)
batch_size = 16
num_epochs = [20, 20]  # Phase 1 and 2 epochs
initial_lr = 1e-4 #1e-5 
fine_tune_lr = 1e-4 #1e-6
#so we can reproduce this same values and stuff
seed = 3
tf.random.set_seed(seed)

# Directory validation
def check_directories():
    """Verify directory structure and return valid paths"""
    if not os.path.exists(train_dir):
        raise ValueError(f"Training directory not found: {train_dir}")
    if not os.path.exists(val_dir):
        raise ValueError(f"Validation directory not found: {val_dir}")
    return train_dir, val_dir

train_dir, val_dir = check_directories()

# ================== Data Pipeline ==================

# Remove validation_split
train_datagen = ImageDataGenerator(
#change to between 0 and 1 (makes the model faster )
#helps find the minimum cuz it reduces skewness
    rescale=1./255,
    rotation_range=45,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    vertical_flip=True,
    brightness_range=[0.7, 1.3],
    fill_mode='reflect'#mirror to fill missing values 
)

#we dont change these(no augmentation)
val_datagen = ImageDataGenerator(rescale=1./255)

# Create balanced data generators
# Training generator 
train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=True,
    seed=seed
)

# Validation generator
val_data = val_datagen.flow_from_directory(
    val_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False
)

print(f"\nFound {train_data.samples} training images across {train_data.num_classes} classes")
print(f"Class labels: {train_data.class_indices}")

# Get class info
num_classes = train_data.num_classes
class_indices = train_data.class_indices
class_names = list(class_indices.keys())

# Compute class weights for imbalanced data 
class_weights = compute_class_weight('balanced', classes=np.unique(train_data.classes), y=train_data.classes)
#0:0.12 {index:weight}
class_weights = dict(enumerate(class_weights))

print(f"\nFound {train_data.samples} training images across {num_classes} classes")
print(f"Class distribution: {class_indices}")

# ================== Model Architecture ==================
def build_model():
    """Build optimized model with MobileNetV2 backbone"""
    base_model = MobileNetV2(
        #user pre trained weights to be faster 
        weights='imagenet',
        #removes top (its the part for classyfication (so we can use our own))
        include_top=False,
        #std input size 
        input_shape=(224, 224, 3),
        #adds global max pooling to reduce spatial dim 
        pooling='max' # makes value of the specified block (pool of values) 2x2
    )
    
    # Freeze all layers initially (wieghts wont be updated) these layers are task specified so we stop them and use our own
    base_model.trainable = False
    #(edges and textures are achived via the first layers so we only change the later ones to adapt to our dataset )
    for layer in base_model.layers[-50:]:  # freez the top ( first ones so we we dont change useful weights)) but the last to adapt the model to our dataset 
        layer.trainable = True

    model = models.Sequential([
        base_model,
        #make sure no negative values get to relu (to avoid dying neurons) -> (standarization makes the value ceneterd around 0 (less negative) specifically 50% neg and 50% pos)
        layers.BatchNormalization(),
        #turn off 70% of the neruons so we avoid overfitting 
        layers.Dropout(0.7),
        #dense = fully connected 
        layers.Dense(256, 
                     #max between 0 and x ( 0 or positive number is the output )
                    activation='relu',
                    #penalize loss based on square of weights (lower weights cuz they hurt loss) to prevent overfitting
                    #gets rid of exploding gradients too
                    kernel_regularizer=regularizers.l2(1e-3)),
        #this one is used to make training faster and less prone to overfitting (adds noise to activation / grd smoothly flow (by stablizing))
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        #used in multiclassification
        #e^zi/all 'e'es ( prob of e among all e class/classes)
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile with label smoothing to prevent overconfidence
    model.compile(
        #we use clipnorm (clipping) (max grd =1) to get rid of exploding gradients  (adam uses adaptive learning rates (avoids local minimum and speeds up training in addition to stabalizing in each step)) good default settings 
        optimizer=Adam(learning_rate=initial_lr, clipnorm=1.0),
        
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=[
            'accuracy',
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall'),
            tf.keras.metrics.AUC(name='auc')
        ]
    )
    return model

# ================== Training Setup ==================
# Callbacks
callbacks = [
    #stop if no improving 
    EarlyStopping(
        monitor='val_loss',
        patience=8,
        restore_best_weights=True,
        verbose=1
    ),
    #reduce learning rate when progress stalls 
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=4,
        min_lr=1e-7,
        verbose=1
    ),
    #save best model
    ModelCheckpoint(
        'best_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )
]

# Build and train model
model = build_model()

# Phase 1: Train top layers
print("\nPhase 1: Training top layers...")
history1 = model.fit(
    train_data,
    epochs=num_epochs[0],
    validation_data=val_data,
    class_weight=class_weights,
    callbacks=callbacks
)

# Phase 2: Fine-tune base model
print("\nPhase 2: Fine-tuning base model...")
# Recompile with lower learning rate
model.compile(
    optimizer=Adam(learning_rate=fine_tune_lr, clipnorm=1.0),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
    metrics=[
        'accuracy',
        tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall'),
        tf.keras.metrics.AUC(name='auc')
    ]
)

history2 = model.fit(
    train_data,
    epochs=num_epochs[1],
    validation_data=val_data,
    class_weight=class_weights,
    callbacks=callbacks
)

# Save final model
model.save('plant_disease_model.h5')
print("Model saved as 'plant_disease_model.h5'")

# ================== Visualization ==================
def plot_training_history(hist1, hist2):
    """Plot combined training history"""
    full_hist = {}
    for k in hist1.history:
        full_hist[k] = hist1.history[k] + hist2.history[k]
    
    plt.figure(figsize=(16, 6))
    
    # Accuracy
    plt.subplot(1, 3, 1)
    plt.plot(full_hist['accuracy'], label='Train Accuracy')
    plt.plot(full_hist['val_accuracy'], label='Val Accuracy')
    plt.title('Training & Validation Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend()
    
    # Loss
    plt.subplot(1, 3, 2)
    plt.plot(full_hist['loss'], label='Train Loss')
    plt.plot(full_hist['val_loss'], label='Val Loss')
    plt.title('Training & Validation Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    
    # Metrics
    plt.subplot(1, 3, 3)
    plt.plot(full_hist['precision'], label='Train Precision')
    plt.plot(full_hist['val_precision'], label='Val Precision')
    plt.plot(full_hist['recall'], label='Train Recall')
    plt.plot(full_hist['val_recall'], label='Val Recall')
    plt.title('Training Metrics')
    plt.ylabel('Score')
    plt.xlabel('Epoch')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('training_plots.png')
    plt.show()

plot_training_history(history1, history2)

# ================== Evaluation ==================
def generate_evaluation_report(model, val_data):
    """Generate detailed evaluation metrics"""
    y_true = val_data.classes
    y_pred_probs = model.predict(val_data)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig('confusion_matrix.png')
    plt.show()
    
    # Classification Report
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=class_names))
    
    # Save metrics
    metrics = {
        'class_names': class_names,
        'class_indices': class_indices,
        'num_classes': num_classes,
        'batch_size': batch_size,
        'image_size': img_size,
        'best_val_accuracy': max(history1.history['val_accuracy'] + history2.history['val_accuracy']),
        'best_val_loss': min(history1.history['val_loss'] + history2.history['val_loss'])
    }
    
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)

generate_evaluation_report(model, val_data)

# ================== Prediction ==================
def predict_image(img_path, model, class_names=class_names, target_size=img_size):
    """Predict disease from image file"""
    try:
        img = load_img(img_path, target_size=target_size)
        img_array = img_to_array(img) / 255.0
        img_batch = np.expand_dims(img_array, axis=0)
        
        prediction = model.predict(img_batch, verbose=0)
        predicted_class = np.argmax(prediction[0])
        confidence = float(np.max(prediction[0]))
        
        return {
            'predicted_class': class_names[predicted_class],
            'confidence': confidence,
            'raw_prediction': prediction.tolist()
        }
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    test_img = 'dataset/validation/rust/rust234.jpeg'
    result = predict_image(test_img, model)
    print(f"Prediction: {result['predicted_class']} ({result['confidence']:.2%})")