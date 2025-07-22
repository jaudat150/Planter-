from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import BlogPost, Comment, Notification, Report
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse


@login_required
def blogs(request):
    posts = request.user.blogpost_set.all()
    unread_notifications = request.user.notification_set.filter(read=False).count()
    return render(request, 'blogs/blogs.html', {
        "posts": posts,
        "unread_notifications": unread_notifications
    })

@login_required
def post_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    unread_notifications = request.user.notification_set.filter(read=False).count()
    return render(request, 'blogs/post_list.html', {
        'posts': posts,
        'unread_notifications': unread_notifications
    })

@login_required
def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    unread_notifications = request.user.notification_set.filter(read=False).count()
    return render(request, 'blogs/post_detail.html', {
        'post': post,
        'unread_notifications': unread_notifications
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
@login_required
def like_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    user = request.user

    liked = False
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
        liked = True

        # Notify author if not self
        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                message=f"{user.username} liked your post '{post.title}'"
            )

    return JsonResponse({
        'liked': liked,
        'total_likes': post.likes.count(),
    })
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BlogPost, Comment, Notification

@login_required
def add_comment(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        profile = request.user.profile
        if profile.is_banned and profile.ban_expiry and timezone.now() < profile.ban_expiry:
            remaining_time = profile.ban_expiry - timezone.now()
            total_seconds = int(remaining_time.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            message = f"You are banned. Try again in {minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}."
            return JsonResponse({'error': message}, status=403)

        text = request.POST.get('text')
        if not text:
            return JsonResponse({'error': 'Comment text is required'}, status=400)
        
        comment = Comment.objects.create(post=post, author=request.user, text=text)
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                message=f"{request.user.username} commented on your post '{post.title}': {text[:30]}..."
            )
        return JsonResponse({
            'success': True,
            'comment': {
                'author': request.user.username,
                'text': comment.text,
                'created_at': comment.created_at.strftime('%B %d, %Y %H:%M'),
            }
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def del_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    
    if request.method == 'POST':
        if comment.author == request.user:
            comment.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return HttpResponseRedirect(reverse('post_detail', args=[comment.post.pk]))
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'You are not the author'}, status=403)
    
    return HttpResponseRedirect(reverse('post_list'))


from django.utils import timezone

@login_required
def create_post(request):
    profile = request.user.profile
    if profile.is_banned and profile.ban_expiry and timezone.now() < profile.ban_expiry:
        remaining_time = profile.ban_expiry - timezone.now()
        total_seconds = int(remaining_time.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        message = f"You are banned and cannot post. Time remaining: {minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}."
        messages.error(request, message)
        return redirect('post_list')
    
    unread_notifications = request.user.notification_set.filter(read=False).count()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if title and content:
            post = BlogPost.objects.create(
                title=title,
                content=content,
                author=request.user,
                image=image,
                created_at=timezone.now()
            )
            return redirect('post_detail', pk=post.pk)
    return render(request, 'blogs/post_form.html', {
        'unread_notifications': unread_notifications
    })

@login_required
def del_confirm(request, id):
    post = get_object_or_404(BlogPost, id=id)
    if post.author != request.user and request.user.profile.role != 'admin':
            return redirect('blogs') 
    unread_notifications = request.user.notification_set.filter(read=False).count()
    return render(request, 'blogs/delete_confirm.html', {
        'post': post,
        'unread_notifications': unread_notifications
    })

@login_required
def del_post(request, id):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, id=id)
        if post.author != request.user and request.user.profile.role != 'admin':
            return redirect('blogs')
        
        if post.image:
            post.image.delete()
        
        post.delete()
        return redirect('post_list')
    
    return redirect('blogs')

@login_required
def edit_post(request, id):
    post = get_object_or_404(BlogPost, id=id)
    unread_notifications = request.user.notification_set.filter(read=False).count()

    if post.author != request.user:
        return redirect('blogs')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        remove_image = request.POST.get('remove_image') == '1'

        if title and content:
            post.title = title
            post.content = content
            post.updated_at = timezone.now()

            if remove_image:
                post.image.delete(save=False)
                post.image = None
            elif 'image' in request.FILES:
                post.image = request.FILES['image']

            post.save()
            return redirect('post_detail', pk=post.id)

    return render(request, 'blogs/edit_post.html', {
        'post': post,
        'unread_notifications': unread_notifications
    })

@login_required
def report_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    unread_notifications = request.user.notification_set.filter(read=False).count()
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if not reason:
            return redirect('post_detail', pk=pk)
        if Report.objects.filter(user=request.user, post=post).exists():
            messages.error(request, "You have already reported this post.")
            return redirect('post_detail', pk=pk)
        Report.objects.create(user=request.user, post=post, reason=reason)
        messages.success(request, "Post reported successfully.")
        return redirect('post_detail', pk=pk)
    return redirect('post_detail', pk=pk)
@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    unread_notifications = request.user.notification_set.filter(read=False).count()
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if not reason:
            return redirect('post_detail', pk=comment.post.pk)
        if Report.objects.filter(user=request.user, comment=comment).exists():
            messages.error(request, "You have already reported this comment.")
            return redirect('post_detail', pk=comment.post.pk)
        Report.objects.create(user=request.user, comment=comment, reason=reason)
        messages.success(request, "Comment reported successfully.")
        return redirect('post_detail', pk=comment.post.pk)
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def notifications(request):
    notifications = request.user.notification_set.all().order_by('-timestamp')
    unread_notifications = request.user.notification_set.filter(read=False).count()
    
    return render(request, 'blogs/notifications.html', {
        'notifications': notifications,
        'unread_notifications': unread_notifications
    })

@login_required
def mark_all_read(request):
    request.user.notification_set.all().update(read=True)
    return redirect('notifications')



from .models import Report, Notification

@login_required
def view_reports(request):
    """Display all reports to admins."""
    if request.user.profile.role != 'admin':  
        return redirect('home')  # Redirect non-admins
    
    reports = Report.objects.all().order_by('-timestamp')
    return render(request, 'blogs/reports.html', {'reports': reports})


from django.utils import timezone
from datetime import timedelta
from accounts.models import BannedEmail

from django.utils import timezone
from datetime import timedelta
from .models import Report, Notification
from django.contrib import messages

@login_required
def send_report(request, report_id):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'
        })

    report = get_object_or_404(Report, id=report_id)

    if request.user.profile.role != 'admin':
        return JsonResponse({
            'success': False,
            'message': 'Permission denied.'
        })

    if report.post:
        recipient = report.post.author
        content_title = report.post.title
    elif report.comment:
        recipient = report.comment.author
        content_title = f"Comment on '{report.comment.post.title}'"
    else:
        return JsonResponse({
            'success': False,
            'message': 'Invalid report.'
        })

    profile = recipient.profile
    profile.strike_count += 1
    message = f"Your content '{content_title}' has been reported."

    if profile.strike_count >= 3:
        profile.is_banned = True
        profile.ban_expiry = timezone.now() + timedelta(minutes=10)
        profile.strike_count = 0
        message = "You have been temporarily banned for 10 minutes due to repeated violations."

    profile.save()

    Notification.objects.create(
        recipient=recipient,
        message=message
    )

    report.delete()

    return JsonResponse({
        'success': True,
        'message': f"Report processed successfully. {recipient.username} has been notified."
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Report
@require_POST
@login_required
def ignore_report(request, report_id):
    if request.user.profile.role != 'admin':
        return JsonResponse({
            'success': False,
            'message': 'Permission denied.'
        })

    try:
        report = Report.objects.get(pk=report_id)
        report.delete()
        return JsonResponse({
            'success': True,
            'message': 'Report ignored and deleted successfully.'
        })
    except Report.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Report not found.'
        })