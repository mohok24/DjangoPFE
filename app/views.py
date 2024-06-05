"""
Definition of views.
"""
from django.contrib import messages
import json
import os
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
from .forms import ReportForm, ReportSearchForm,PatientSearchForm,UploadFileForm
from django.db.models import Max
from app.ai_model import AI
import re
from docx import Document
from django.conf import settings


ai=AI(model_path="threewordtest.h5")
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'home_page.html',
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
                next_url = '/homeres'  
            elif user.role == 'Radiologist':
                next_url = '/homerad'  
            else:
                next_url = '/'  
            print(f"meowab");
            return HttpResponseRedirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            print(f"Authentication failed for user: {username}")

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
    radiologists = User.objects.filter(role='Radiologist')

    for patient in patients_with_reports:
        patient.num_reports = patient.report_set.count()
    context = {
        'patients_with_reports': patients_with_reports,
        'radiologists': radiologists
    
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
        report = Report.objects.filter(patient__radiologists__in=[request.user]).select_related('patient').all()

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
            patient_name = form.cleaned_data.get('patient_name')
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
            if patient_name:
                name_parts = patient_name.split()
                if len(name_parts) == 2:
                    firstname, lastname = name_parts
                    patients = Patient.objects.filter(
                        Q(firstname__icontains=firstname) & Q(lastname__icontains=lastname),
                        radiologists=request.user
                    )
                else:
                    search_name = name_parts[0]
                    patients = Patient.objects.filter(
                        Q(firstname__icontains=search_name) | Q(lastname__icontains=search_name),
                        radiologists=request.user
                    )
                query &= Q(patient__in=patients)
            for field_name, field_value in form.cleaned_data.items():
                if field_name not in ['patient_id','dates', 'from_date', 'to_date','patient_name'] and field_value:
                    if field_name == 'date':
                        query &= Q(date=field_value)
                    else:
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
            return JsonResponse({'error': 'Form data is invalid', 'errors': form.errors})
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
    acr_brad = request.GET.get('acr_brad')

    print("ACR or BIRAD:", acr_brad)

    s_date = request.GET.get('date-min')
    e_date = request.GET.get('date-max')
    age_max = request.GET.get('age-max')
    age_min = request.GET.get('age-min')
    query = Q()

    if s_date:
        query &= Q(date__gte=s_date)
    if e_date:
        query &= Q(date__lte=e_date)
    if age_max:
        query &= Q(age__lte=age_max)
    if age_min:
        query &= Q(age__gte=age_min)

    reports = Report.objects.filter(query)
    print("Reports found:", reports.count())
    
    acr_r, acr_l, acr_b = [], [], []
    time_r, time_l, time_b = [], [], []
    brad_r, brad_l, brad_b = [], [], []

    if acr_brad == 'acr':
        for report in reports:
            print("Report:", report.id)
            if 'type a' in report.rightM.lower():
                acr_r.append('type a')
                time_r.append(report.date)
            elif 'type b' in report.rightM.lower():
                acr_r.append('type b')
                time_r.append(report.date)
            elif 'type c' in report.rightM.lower():
                acr_r.append('type c')
                time_r.append(report.date)
            elif 'type d' in report.rightM.lower():
                acr_r.append('type d')
                time_r.append(report.date)
            
            print("Right M findings:", report.rightM.lower())

            if 'type a' in report.leftM.lower():
                acr_l.append('type a')
                time_l.append(report.date)
            elif 'type b' in report.leftM.lower():
                acr_l.append('type b')
                time_l.append(report.date)
            elif 'type c' in report.leftM.lower():
                acr_l.append('type c')
                time_l.append(report.date)
            elif 'type d' in report.leftM.lower():
                acr_l.append('type d')
                time_l.append(report.date)
            
            print("Left M findings:", report.leftM.lower())

            if 'type a' in report.bothM.lower():
                acr_b.append('type a')
                time_b.append(report.date)
            elif 'type b' in report.bothM.lower():
                acr_b.append('type b')
                time_b.append(report.date)
            elif 'type c' in report.bothM.lower():
                acr_b.append('type c')
                time_b.append(report.date)
            elif 'type d' in report.bothM.lower():
                acr_b.append('type d')
                time_b.append(report.date)

            print("Both M findings:", report.bothM.lower())

    elif acr_brad == 'birad':
        for report in reports:
            print("Report:", report.id)
            if 'bi_rads' in report.rightclassification.lower():
                if '0' in report.rightclassification:
                    brad_r.append('type 0')
                elif '1' in report.rightclassification:
                    brad_r.append('type 1')
                elif '2' in report.rightclassification:
                    brad_r.append('type 2')
                elif '3' in report.rightclassification:
                    brad_r.append('type 3')
                elif '4' in report.rightclassification:
                    brad_r.append('type 4')
                elif '5' in report.rightclassification:
                    brad_r.append('type 5')
                elif '6' in report.rightclassification:
                    brad_r.append('type 6')
                time_r.append(report.date)

                print("Right classification:", report.rightclassification.lower())

            if 'bi_rads' in report.leftclassification.lower():
                if '0' in report.leftclassification:
                    brad_l.append('type 0')
                elif '1' in report.leftclassification:
                    brad_l.append('type 1')
                elif '2' in report.leftclassification:
                    brad_l.append('type 2')
                elif '3' in report.leftclassification:
                    brad_l.append('type 3')
                elif '4' in report.leftclassification:
                    brad_l.append('type 4')
                elif '5' in report.leftclassification:
                    brad_l.append('type 5')
                elif '6' in report.leftclassification:
                    brad_l.append('type 6')
                time_l.append(report.date)

                
                print("Left classification:", report.leftclassification.lower())

            if 'bi_rads' in report.bothclassification.lower() or 'bi-rads' in report.bothclassification.lower():
                if '0' in report.bothclassification:
                    brad_b.append('type 0')
                elif '1' in report.bothclassification:
                    brad_b.append('type 1')
                elif '2' in report.bothclassification:
                    brad_b.append('type 2')
                elif '3' in report.bothclassification:
                    brad_b.append('type 3')
                elif '4' in report.bothclassification:
                    brad_b.append('type 4')
                elif '5' in report.bothclassification:
                    brad_b.append('type 5')
                elif '6' in report.bothclassification:
                    brad_b.append('type 6')
                time_b.append(report.date)

                print("Both classification:", report.bothclassification.lower())

    print("acr_r :", acr_r)
    print("brad_r:", brad_r)
    print("time  :", time_r)
    print("acr_l :", acr_l)
    print("brad_l:", brad_l)
    print("time  :", time_l)
    print("acr_b :", acr_b)
    print("brad_b:", brad_b)
    print("time  :", time_b)

    x_val = request.GET.get("x_val")
    from collections import defaultdict, Counter

    classified_data_r = defaultdict(lambda: defaultdict(Counter))
    classified_data_l = defaultdict(lambda: defaultdict(Counter))
    classified_data_b = defaultdict(lambda: defaultdict(Counter))

    def add_to_classified_data(data, acr_list, time_list):
        for type_, date in zip(acr_list, time_list):
            year = date.strftime('%Y')
            if type_ not in data[year]:
                data[year][type_] = 0
            data[year][type_] += 1
            print(f"Added to data[{year}][{type_}]: {data[year][type_]}")

    classified_data_r = defaultdict(lambda: defaultdict(Counter))
    classified_data_l = defaultdict(lambda: defaultdict(Counter))
    classified_data_b = defaultdict(lambda: defaultdict(Counter))
    
    if acr_r:
        print("acr_r entered to classify")
        add_to_classified_data(classified_data_r, acr_r, time_r)
    if acr_l:
        print("acr_l entered to classify")
        add_to_classified_data(classified_data_l, acr_l, time_l)
    if acr_b:
        print("acr_b entered to classify")
        add_to_classified_data(classified_data_b, acr_b, time_b)
    if brad_r:
        print("birad_r entered to classify")
        add_to_classified_data(classified_data_r, brad_r, time_r)
    if brad_l:
        print("birad_l entered to classify")
        add_to_classified_data(classified_data_l, brad_l, time_l)
    if brad_b:
        print("birad_b entered to classify")
        add_to_classified_data(classified_data_b, brad_b, time_b)

    def defaultdict_to_dict(d):
        if isinstance(d, defaultdict):
            d = {k: defaultdict_to_dict(v) for k, v in d.items()}
        if isinstance(d, Counter):
            d = dict(d)
        return d


    classified_data_r_dict = defaultdict_to_dict(classified_data_r)
    classified_data_l_dict = defaultdict_to_dict(classified_data_l)
    classified_data_b_dict = defaultdict_to_dict(classified_data_b)

    context = {
        'time_range': time_range,
        'reports': reports,
        'classified_data_r': json.dumps(classified_data_r_dict),
        'classified_data_l': json.dumps(classified_data_l_dict),
        'classified_data_b': json.dumps(classified_data_b_dict),
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


from django.http import JsonResponse
import time

def predict(request):
    text = request.POST.get('input_text', '')
    text=AI.preprocess(text)    
    predicted_word=ai.predict_next_word(text,1)
    return JsonResponse({'predicted_text': predicted_word})

def add_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request=request)
        if form.is_valid():
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            age = request.POST.get('age')
            user = request.user
            patient = Patient.objects.filter(
                Q(firstname__icontains=firstname) &
                Q(lastname__icontains=lastname)
            ).first()

            if patient:
                patient.age = age
                patient.save()
            else:
                patient = Patient.objects.create(first_name=firstname, last_name=lastname, age=age)
                patient.radiologists.add(user)
                patient.save()

            report = form.save(commit=False)
            report.patient = patient
            report.save()
            return redirect('reports')  
        else:
            print(form.errors)
    else:

        form = ReportForm(request=request)

    return render(request, 'add_report.html', {'form': form})
    
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('home'))
@login_required
def homeres(request):
    return render(request,'homeres.html')
@login_required
def homerad(request):
    return render(request,'homerad.html')
@login_required
def dashboard(request):
    role = request.user.role
    
    if role == 'Radiologist':
        return render(request, 'homerad.html')
    elif role == 'Researcher':
        return render(request, 'homeres.html')
    else:
        return render(request, 'homeres.html')
    
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_path = os.path.join(settings.MEDIA_ROOT, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            pdf_path = process_and_generate_pdf(file_path)
            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="output.pdf"'
                return response
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

from django.template.loader import render_to_string
from weasyprint import HTML
from .textextraction import classify
def process_and_generate_pdf(file_path):
    data = classify(file_path) 
    
    report = data
    patient = report.patient 

    context = {
        'report': {
            'date': report.date,
            'patient_name': patient.firstname,
            'patient_name2': patient.lastname,
            'patient_age': patient.age,
            'type': report.type,
            'indication': report.indication,
            'recommendation': report.recommendations,
            'leftm': report.leftM,
            'rightm': report.rightM,
            'bothm': report.bothM,
            'lefte': report.leftE,
            'righte': report.rightE,
            'bothe': report.bothE,
            'leftc': report.leftclassification,
            'rightc': report.rightclassification,
            'bothc': report.bothclassification,
            'conc' : report.conclusion
        }
    }
    
    html_string = render_to_string('pdftemplate.html', context)
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'output.pdf')
    HTML(string=html_string).write_pdf(pdf_file_path)
    
    return pdf_file_path
