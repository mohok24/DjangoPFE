"""
Definition of views.
"""

from asyncio.windows_events import NULL
from datetime import datetime
from site import ENABLE_USER_SITE
from sqlite3 import Date
from django.http import HttpRequest,HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, HttpResponseRedirect   
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.template import loader
from django.db.models import Q
from .models import Patient,Report
from django.http import JsonResponse
from app.models import Message
from .forms import ReportForm, ReportSearchForm,PatientSearchForm
from django.db.models import Max

import re


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )



from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def restricted_view(request):
    return HttpResponse("You're logged in!")


def login_view(request):
    

    raw_password = "a"
    hashed_password = make_password(raw_password)

    print(hashed_password)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Attempting to authenticate user: {username}")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"Username: {username}")
            login(request, user)
            
            print(f"User Role: {user.role}")
            
            if user.role == 'Researcher':
                next_url = '/about/'  
            elif user.role == 'Radiologist':
                next_url = '/contact/'  
            else:
                next_url = '/'  
            print(f"meowab");
            return HttpResponseRedirect(next_url)
        else: print(f"Authentication failed for user: {username}")

    return render(request, 'login.html')

def patients(request):
    if(request.user.role=='Radiologist'):
        patients_with_reports = Patient.objects.filter(report__user=request.user).distinct()

        for patient in patients_with_reports:
            patient.num_reports = patient.report_set.count()

        context = {
            'patients_with_reports': patients_with_reports
        }

        return render(request, 'patient.html', context) 
    else:
        patients_with_reports = Patient.objects.all()
        for patient in patients_with_reports:
            patient.num_reports = patient.report_set.count()

        context = {
            'patients_with_reports': patients_with_reports
        }

        return render(request, 'patient2.html', context) 
        
def all_patients(request):
    patients_with_reports = Patient.objects.all()

    for patient in patients_with_reports:
        patient.num_reports = patient.report_set.count()

    context = {
        'patients_with_reports': patients_with_reports
    }

    return render(request, 'patient2.html', context) 

def details(request, id):
  patient= Patient.objects.get(id=id)
  user_role = request.user.role 
  patient.num_reports = patient.report_set.count()
  if user_role == 'Researcher':
        template_name = 'details_researcher.html'
  else:
        template_name = 'details.html'

  template = loader.get_template(template_name)
  reports = Report.objects.filter(patient = patient)

  birad_keys = ["0", "1", "2", "3", "4", "5", "6"]
  pattern = r'[1-6](?:[abc])?'

  x_values = [report.date.isoformat() for report in reports]
  y_values = []
  latest_report_date_only = Report.objects.filter(patient=patient).aggregate(latest_date=Max('date'))['latest_date']

  

  y_values = []
  for report in reports:
    right=-1
    left=-1
    both=-1
    bothclassification_lower = report.bothclassification.lower()
    leftclassification_lower = report.leftclassification.lower()
    rightclassification_lower = report.rightclassification.lower()
    bothmatches = re.findall(pattern, bothclassification_lower) 
    leftmatches = re.findall(pattern, leftclassification_lower) 
    rightmatches = re.findall(pattern, rightclassification_lower) 
    if rightmatches:
         right=int(rightmatches[0])
    if leftmatches:
         left=int(leftmatches[0])
    if bothmatches:
        both=int(bothmatches[0])
    y_values.append([right,left,both])





  context = {
    'patient': patient,
    'reports' : reports,
    'x_values': x_values,
    'y_values': y_values,
    'date':latest_report_date_only
  }
  return HttpResponse(template.render(context, request))

@login_required
def reports(request):
    if (request.user.role=='Radiologist'):
        report = Report.objects.filter(user=request.user).select_related('patient').all()

        context = {
        'report': report
        }

        return render(request, 'reports.html', context)
    else:
        report = Report.objects.select_related('patient').all()

        context = {
        'report': report
        }
        return render(request,'reports2.html',context)

def all_reports(request):
    radiologists = User.objects.filter(role='Radiologist')

    report = Report.objects.select_related('patient').all()

    context = {
        'report': report,
        'radiologists': radiologists
    }

    return render(request, 'reports2.html', context)

def rdetails(request, id):
  report= Report.objects.get(id=id)
  user_role = request.user.role 

  if user_role == 'Researcher':
        template_name = 'rdetails.html'
  else:
        template_name = 'rdetails.html'

  template = loader.get_template(template_name)
  context = {
    'report': report,
  }
  return HttpResponse(template.render(context, request))



def report_search(request):
    reports = Report.objects.all()
    
    if request.method == 'GET':
        form = ReportSearchForm(request.GET)
        if form.is_valid():
            query = Q()
            patient_id = form.cleaned_data.get('patient_id')
            dates_choice = form.cleaned_data.get('dates')
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            date = form.cleaned_data.get('date')
            print(dates_choice)
            
            if patient_id:
                query &= Q(patient_id=patient_id)
            if dates_choice == 'exact' and date:
                query &= Q(date=date)
            elif dates_choice == 'range' and from_date and to_date:
                query &= Q(date__range=[from_date, to_date])

            for field_name, field_value in form.cleaned_data.items():
                if field_name not in ['patient_id','dates', 'from_date', 'to_date'] and field_value:
                    if field_name == 'date':
                        query &= Q(date=field_value)
                    else:
                        print(field_name," ",field_value)
                        query &= Q(**{field_name + '__icontains': field_value})

            reports = Report.objects.filter(query)
    else:
        form = ReportSearchForm()

    context = {
        'form': form,
        'reports': reports
    }
    return render(request, 'report_search.html', context)

def patient_search(request):
    patients = Patient.objects.all()
    
    if request.method == 'GET':
        form = PatientSearchForm(request.GET)
        if form.is_valid():
            query = Q()  
            
            for field_name, field_value in form.cleaned_data.items():
               if field_name not in ['query'] and field_value:
                     query &= Q(**{field_name + '__icontains': field_value})
                     print(field_value) 
           
            patients = Patient.objects.filter(query)
            for patient in patients:
                patient.num_reports = patient.report_set.count()
    else:
        form = PatientSearchForm()

    context = {
        'form': form,
        'patients': patients
    }
    return render(request, 'patient_search.html', context)


from django.shortcuts import render
from django.http import JsonResponse
from app.models import User 
from app.models import Message
from app.forms import MessageForm

from django.http import JsonResponse
from .forms import MessageForm
from .models import User, Message

def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            recipient_username = form.cleaned_data['receiver']
            message_content = form.cleaned_data['content']
            image = form.cleaned_data['image']

            print("Recipient username:", recipient_username)
            print("Message content:", message_content)
            print("Image:", image)

            try:
                recipient = User.objects.get(username=recipient_username)
                print("Recipient:", recipient)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Recipient not found'})

            message = Message(sender=request.user, receiver=recipient, content=message_content)
            if image:
                message.image = image
            message.save()

            return JsonResponse({'message': 'Message sent successfully'})
        else:
            return JsonResponse({'error': 'Form data is invalid'})
    else:
        receiver = request.GET.get('receiver')
        form = MessageForm(initial={'receiver': receiver}) 
        return render(request, 'chat.html', {'form': form})


from .models import Message

def receive_message(request):
    messages = Message.objects.filter(receiver=request.user)

    message_data = []
    for message in messages:
        message_dict = {
            'id':message.id,
            'sender_username': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp,
            'image_url': message.image.url if message.image else None,
        }
        message_data.append(message_dict)

    return render(request, 'receive_messages.html', {'messages': message_data})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Message


def delete_message(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        message_id = request.POST.get('message_id')
        message = Message.objects.filter(pk=message_id).first()

        if message and message.receiver == request.user:
            message.delete()
            return JsonResponse({'message': 'Message deleted successfully.'})
        else:
            return JsonResponse({'error': 'Unable to delete message.'}, status=400)

    return JsonResponse({'error': 'Invalid request method or not an AJAX request.'}, status=400)

from datetime import datetime, timedelta
from django.db.models import Count
from django.shortcuts import render
from .models import Report

def statistics(request):
    time_range = request.GET.get('time_range', 'all_time')

    if time_range == 'past_week':
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
    elif time_range == 'past_month':
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif time_range == 'past_year':
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
    else:
        start_date = None
        end_date = None

    if start_date and end_date:
        reports = Report.objects.filter(date__range=[start_date, end_date])
    else:
        reports = Report.objects.all()

    num_reports = reports.count()
    num_patients = reports.values('patient').distinct().count()
    avg_age = reports.aggregate(avg_age=Count('patient__age'))['avg_age']

    context = {
        'time_range': time_range,
        'num_reports': num_reports,
        'num_patients': num_patients,
        'avg_age': avg_age,
        'reports':reports
    }
    return render(request, 'statistics.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Message

@login_required
def message_details(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    if request.user != message.receiver:
        return HttpResponseForbidden("You are not authorized to view this message.")
    
    return render(request, 'message_details.html', {'message': message})

def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'profile.html', {'user': user})

from datetime import datetime, timedelta
from django.db.models import Count
from django.shortcuts import render
from .models import Report

def statistics(request):
    time_range = request.GET.get('time_range', 'all_time')
    graph1_timerange = request.GET.get('time_range_g1', 'all_time')
    graph2_timerange = request.GET.get('time_range_g2', 'all_time')

    # Define the start and end dates based on the selected time range
    if time_range == 'past_week':
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
    elif time_range == 'past_month':
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif time_range == 'past_year':
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
    else:
        start_date = None
        end_date = None

    #time for graph 1
    if graph1_timerange == 'past_week':
        start_date1 = datetime.now() - timedelta(days=7)
        end_date1 = datetime.now()
    elif graph1_timerange == 'past_month':
        start_date1 = datetime.now() - timedelta(days=30)
        end_date1 = datetime.now()
    elif graph1_timerange == 'past_year':
        start_date1 = datetime.now() - timedelta(days=365)
        end_date1 = datetime.now()
    else:
        start_date1 = None
        end_date1 = None

    #time range graph 2
    if graph2_timerange == 'past_week':
        start_date2 = datetime.now() - timedelta(days=7)
        end_date2 = datetime.now()
    elif graph2_timerange == 'past_month':
        start_date2 = datetime.now() - timedelta(days=30)
        end_date2 = datetime.now()
    elif graph2_timerange == 'past_year':
        start_date2 = datetime.now() - timedelta(days=365)
        end_date2 = datetime.now()
    else:
        start_date2 = None
        end_date2 = None

    # Filter reports based on the selected time range
    if start_date and end_date:
        reports = Report.objects.filter(date__range=[start_date, end_date])
    else:
        reports = Report.objects.all()
    
    #graph1
    if start_date and end_date:
        reports_g1 = Report.objects.filter(date__range=[start_date, end_date])
    else:
        reports_g1 = Report.objects.all()

    #graph2
    if start_date and end_date:
        reports_g2 = Report.objects.filter(date__range=[start_date, end_date])
    else:
        reports_g2 = Report.objects.all()

    # Calculate statistics
    num_reports = reports.count()
    num_patients = reports.values('patient').distinct().count()
    avg_age = reports.aggregate(avg_age=Count('patient__age'))['avg_age']

    # Pass data to the template
    context = {
        'time_range': time_range,
        'num_reports': num_reports,
        'num_patients': num_patients,
        'avg_age': avg_age,
        'reports':reports,
        'reports_g1':reports_g1,
        'reports_g2':reports_g2,
    }
    return render(request, 'statistics.html', context)


from django.http import JsonResponse
import time

def predict(request):
    input_text = request.POST.get('input_text', '')

    dummy_predicted_text = "This is a predicted text from the AI model."

    return JsonResponse({'predicted_text': dummy_predicted_text})

def add_report(request):
    if request.method == 'POST':
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': report_form.errors})
    else:
        report_form = ReportForm()
        return render(request, 'add_report.html', {'report_form': report_form})