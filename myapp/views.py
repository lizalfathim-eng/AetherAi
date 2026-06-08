import os
import smtplib

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group


# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from myapp.models import Upload, Staff, Complaint


def loginpage_get(request):
    return render(request, "login.html")


def loginpage_post(request):
    username=request.POST['username']
    password=request.POST['password']
    if not username or not password:
        messages.warning(request,'username and password must be required')
        return redirect('/myapp/loginpage_get/')
    check=authenticate(request,username=username,password=password)
    if check is not None:
        login(request,check)
        if check.groups.filter(name='Admin').exists():
            return redirect('/myapp/new_home/')
        elif check.groups.filter(name='Staff').exists():
            return redirect('/myapp/s_home_get/')
        else:
            messages.warning(request,'invalid user')
            return redirect('/myapp/loginpage_get/')
    else:
        messages.warning(request, 'invalid username or password')
        return redirect('/myapp/loginpage_get/')

def logout_get(request):
    logout(request)
    return redirect('/myapp/loginpage_get/')

@login_required(login_url='/myapp/loginpage_get/')
def home_get(request):
    return render(request,'admin/home_index.html')

@login_required(login_url='/myapp/loginpage_get/')
def new_home(request):
    data=Upload.objects.all().order_by('-id')
    return render(request,'admin/home_index.html',{'data':data})

@login_required(login_url='/myapp/loginpage_get/')
def change_password_get(request):
    return render(request, 'admin/change_password.html')

@login_required(login_url='/myapp/loginpage_get/')
def change_password_post(request):
    old_password = request.POST['password1']
    new_password = request.POST['password2']
    confirm_password = request.POST['password3']
    data = request.user
    if data.check_password(old_password):
        if new_password == confirm_password:
            data.set_password(new_password)
            data.save()
            return redirect('/myapp/loginpage_get/')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('/myapp/change_password_get/#abc')
    else:
        messages.error(request, 'Invalid Password')
        return redirect('/myapp/change_password_get/#abc')

@login_required(login_url='/myapp/loginpage_get/')
def add_staff(request):
    from datetime import datetime
    date=datetime.now().date()
    return render(request,'admin/add_staff.html',{'date':date})

@login_required(login_url='/myapp/loginpage_get/')
def add_staff_post(request):
    name=request.POST['name']
    dob=request.POST['dob']
    gender=request.POST['gender']
    email=request.POST['email']
    phone=request.POST['phone']
    qualification=request.POST['qualification']
    place=request.POST['place']
    pin=request.POST['pin']
    district=request.POST['district']
    photo=request.FILES['photo']
    join=request.POST['jdate']
    experience=request.POST['experience']
    designation=request.POST['designation']
    salary=request.POST['salary']
    status=request.POST['status']
    dep=request.POST['deparment']
    from datetime import datetime
    # password = '1234'

    if User.objects.filter(username=email).exists():
        messages.error(request, 'Email Exists')
        return redirect('/myapp/add_staff/#abc')

    import random
    new_pass = random.randint(000000, 999999)
    server = smtplib.SMTP('smtp.gmail.com', 587)

    server.starttls()
    server.login("aetheraiengine@gmail.com", "mmgk hzkx haqq cvhy")  # App Password
    to = email
    subject = "Test Email"
    body = "Your new password is " + str(new_pass)
    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail("s@gmail.com", to, msg)
    # Disconnect from the server
    server.quit()

    a = User.objects.create_user(username=email, password=new_pass)
    a.groups.add(Group.objects.get(name='Staff'))
    a.save()

    fs = FileSystemStorage()
    date = datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
    fs.save(date, photo)
    path = fs.url(date)

    s=Staff()
    s.name=name
    s.dob=dob
    s.gender=gender
    s.email=email
    s.phone=phone
    s.qualification=qualification
    s.place=place
    s.pin=pin
    s.district=district
    s.photo=path
    s.join_date=join
    s.experience=experience
    s.designation=designation
    s.salary=salary
    s.status=status
    s.department=dep
    s.USER=a
    s.save()

    messages.error(request, 'Added succesfully')
    return redirect('/myapp/add_staff/#abc')

@login_required(login_url='/myapp/loginpage_get/')
def view_staff(request):
    data=Staff.objects.all()
    return render(request,'admin/view_staff.html',{'data':data})

@login_required(login_url='/myapp/loginpage_get/')
def view_more_staff(request,id):
    data=Staff.objects.get(id=id)
    return render(request,'admin/view_more_staff.html',{'data':data})

@login_required(login_url='/myapp/loginpage_get/')
def edit_staff(request,id):
    data=Staff.objects.get(id=id)
    return render(request,'admin/edit_staff.html',{'data':data})

@login_required(login_url='/myapp/loginpage_get/')
def  edit_staff_post(request):
    id=request.POST['id']
    name = request.POST['name']
    dob = request.POST['dob']
    gender = request.POST['gender']
    email = request.POST['email']
    phone = request.POST['phone']
    qualification = request.POST['qualification']
    place = request.POST['place']
    pin = request.POST['pin']
    district = request.POST['district']
    join = request.POST['jdate']
    experience = request.POST['experience']
    designation = request.POST['designation']
    salary = request.POST['salary']
    status = request.POST['status']
    dep = request.POST['deparment']



    s = Staff.objects.get(id=id)
    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        from datetime import datetime
        fs = FileSystemStorage()
        date = datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
        fs.save(date, photo)
        path = fs.url(date)
        s.photo = path

    s.name = name
    s.dob = dob
    s.gender = gender
    s.email = email
    s.phone = phone
    s.qualification = qualification
    s.place = place
    s.pin = pin
    s.district = district
    s.join_date = join
    s.experience = experience
    s.department = dep
    s.designation = designation
    s.salary = salary
    s.status = status
    s.department = dep
    s.save()
    messages.error(request, 'Updated succesfully')
    return redirect('/myapp/view_staff/#abc')

@login_required(login_url='/myapp/loginpage_get/')
def delete_staff(request,id):
    Staff.objects.filter(USER_id=id).delete()
    User.objects.filter(id=id).delete()
    return redirect('/myapp/view_staff/#abc')



@login_required(login_url='/myapp/login/')
def adm_view_complaint(request):
    data=Complaint.objects.all()
    # l=[]
    # for i in data:
    #     a=User.objects.get(id=i.AUTHUSER.id)
    #     if Authority.objects.filter(AUTHUSER=a.id).exists():
    #         aa=Authority.objects.get(AUTHUSER=i.AUTHUSER.id).authorityname
    #         l.append({
    #             'id':i.id,
    #             'name':aa,
    #             'date':i.date,
    #             'complaint':i.complaint,
    #             'reply':i.reply,
    #             'status':i.status,
    #             'type':'authority'
    #
    #
    #         })
    #     elif Police.objects.filter(USER=a.id).exists():
    #         aa = Police.objects.get(USER=i.AUTHUSER.id).name
    #         l.append({
    #             'id': i.id,
    #             'name': aa,
    #             'date': i.date,
    #             'complaint': i.complaint,
    #             'reply': i.reply,
    #             'status': i.status,
    #             'type':'police'
    #
    #         })
    return render(request,'admin/viewcomplaint.html',{'data':data})

@login_required(login_url='/myapp/login/')
def send_reply(request,id):
    return render(request,'admin/send reply.html',{'id':id})

@login_required(login_url='/myapp/login/')
def send_reply_post(request):
    id=request.POST['id']
    reply=request.POST['reply']
    Complaint.objects.filter(id=id).update(status='replied',reply=reply)
    return redirect('/myapp/adm_view_complaint/#abc')



#============

@login_required(login_url='/myapp/loginpage_get/')
def s_home_get(request):
    return render(request,'staff/s_home_index.html')


@login_required(login_url='/myapp/login/')
def staff_view_profile_get(request):
    a=Staff.objects.get(USER=request.user.id)
    return render(request,"staff/view_profile.html",{'data':a})


@login_required(login_url='/myapp/loginpage_get/')
def view_staff_more(request,id):
    data=Staff.objects.get(id=id)
    return render(request,'staff/view_more_staff.html',{'data':data})


@login_required(login_url='/myapp/loginpage_get/')
def s_change_password_get(request):
    return render(request, 'staff/change_password.html')

@login_required(login_url='/myapp/loginpage_get/')
def s_change_password_post(request):
    old_password = request.POST['password1']
    new_password = request.POST['password2']
    confirm_password = request.POST['password3']
    data = request.user
    if data.check_password(old_password):
        if new_password == confirm_password:
            data.set_password(new_password)
            data.save()
            return redirect('/myapp/loginpage_get/')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('/myapp/s_change_password_get/#abc')
    else:
        messages.error(request, 'Invalid Password')
        return redirect('/myapp/s_change_password_get/#abc')

@login_required(login_url='/myapp/login/')
def view_complaintreply_get(request):
    data=Complaint.objects.filter(STAFF__USER_id=request.user.id)
    return render(request,"staff/view_complaintreply.html",{'data':data})

@login_required(login_url='/myapp/login/')
def sendcomplaint_admin_get(request):
    return render(request, "staff/send_complaint.html")

@login_required(login_url='/myapp/login/')
def sendcomplaint_admin_post(request):
    complaint = request.POST['complaint']
    from datetime import datetime

    obj = Complaint()
    obj.reply = 'pending'
    obj.status = "pending"
    obj.date = datetime.now().date()
    obj.complaint = complaint
    obj.STAFF = Staff.objects.get(USER_id=request.user.id)
    obj.save()

    return redirect("/myapp/view_complaintreply_get/#abc")

@login_required(login_url='/myapp/loginpage_get/')
def upload_file(request):
    return render(request, 'staff/upload_file.html')


# @login_required(login_url='/myapp/loginpage_get/')
# def upload_file_post(request):
#     file=request.FILES['file']
#     from datetime import datetime
#     fs = FileSystemStorage()
#     date = datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
#     fs.save(date, file)
#     path = fs.url(date)
#
#     a=Upload()
#     a.document=path
#     a.Date=datetime.now().today()
#     a.STAFF=Staff.objects.get(USER_id=request.user.id)
#     a.save()
#     return redirect('/myapp/upload_file/#abc')

# @login_required(login_url='/myapp/loginpage_get/')
# def upload_file_post(request):
#
#     file = request.FILES.get('file')
#     if not file:
#         return redirect('/myapp/upload_file/')
#
#     # Allowed file extensions
#     allowed_extensions = [
#         '.jpg', '.jpeg', '.png',
#         '.pdf',
#         '.doc', '.docx',
#         '.xls', '.xlsx',
#         '.csv'
#     ]
#
#     # Get original file extension
#     ext = os.path.splitext(file.name)[1].lower()
#
#     if ext not in allowed_extensions:
#         # Optional: add message framework here
#         return redirect('/myapp/upload_file/')
#
#     fs = FileSystemStorage()
#     from datetime import datetime
#
#     # Create unique filename with original extension
#     filename = datetime.now().strftime('%Y%m%d%H%M%S') + ext
#     fs.save(filename, file)
#
#     path = fs.url(filename)
#
#     a = Upload()
#     a.document = path
#     a.Date = datetime.now()
#     a.STAFF = Staff.objects.get(USER_id=request.user.id)
#     a.save()
#
#     return redirect('/myapp/upload_file/#abc')
# def upload_file_post(request):
#     import os
#     import hashlib
#     from django.core.files.storage import FileSystemStorage
#     from datetime import datetime
#     from django.shortcuts import redirect
#     from .models import Upload, Staff
#
#     file = request.FILES.get('file')
#     if not file:
#         return redirect('/myapp/upload_file/#abc')
#
#     # Allowed file extensions
#     allowed_extensions = [
#         '.jpg', '.jpeg', '.png',
#         '.pdf',
#         '.doc', '.docx',
#         '.xls', '.xlsx',
#         '.csv'
#     ]
#
#     # Get original file extension
#     ext = os.path.splitext(file.name)[1].lower()
#
#     if ext not in allowed_extensions:
#         return redirect('/myapp/upload_file/#abc')
#
#     # ===============================
#     # 🔹 PLAGIARISM / DUPLICATE CHECK
#     # ===============================
#
#     # Generate SHA256 hash of file
#     hasher = hashlib.sha256()
#     for chunk in file.chunks():
#         hasher.update(chunk)
#     file_hash = hasher.hexdigest()
#
#     # Reset file pointer after reading
#     file.seek(0)
#
#     # Check if hash already exists in database
#     if Upload.objects.filter(hashvalue=file_hash).exists():
#         print("Duplicate File Detected!")
#         messages.error(request,'Duplicate File Detected!')
#         return redirect('/myapp/upload_file/#abc')
#
#     # ===============================
#     # 🔹 SAVE FILE (ONLY IF NOT DUPLICATE)
#     # ===============================
#
#     fs = FileSystemStorage()
#
#     # Create unique filename with original extension
#     filename = datetime.now().strftime('%Y%m%d%H%M%S') + ext
#     fs.save(filename, file)
#
#     path = fs.url(filename)
#
#     extracted_text = ""
#
#     # -------- PDF --------
#     if path.lower().endswith(".pdf"):
#         reader = PdfReader(full_path)
#         for page in reader.pages:
#             text = page.extract_text()
#             if text:
#                 extracted_text += text + "\n"
#
#     # -------- CSV --------
#     elif file_path.lower().endswith(".csv"):
#         with open(full_path, newline="", encoding="utf-8") as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 extracted_text += " | ".join(row) + "\n"
#
#     # -------- IMAGE (OCR) --------
#     elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
#         image = Image.open(full_path)
#         extracted_text = pytesseract.image_to_string(image)
#
#     else:
#         extracted_text = "Unsupported file format"
#
#     a = Upload()
#     a.document = path
#     a.Date = datetime.now()
#     a.STAFF = Staff.objects.get(USER_id=request.user.id)
#     a.hashvalue = file_hash   # ✅ save hash value
#
#     a.save()
#
#     messages.success(request,'File Uploaded Successfully...')
#     return redirect('/myapp/upload_file/#abc')





import numpy as np
import faiss
import re
import os
import pickle
from sentence_transformers import SentenceTransformer

# ======================================================
# SETTINGS
# ======================================================
JSON_PATH = r"C:\AetherAI\AetherAI\media\uploaded_data.json"
INDEX_PATH = "legal_index.faiss"
METADATA_PATH = "metadata.pkl"
PROCESSED_IDS_PATH = "processed_ids.pkl"

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

# ======================================================
# LOAD MODEL
# ======================================================
print("Loading model...")
model = SentenceTransformer(MODEL_NAME)






def upload_file_post(request):
    import os
    import json
    import hashlib
    import csv
    from datetime import datetime
    from django.core.files.storage import FileSystemStorage
    from django.shortcuts import redirect
    from django.contrib import messages
    from PyPDF2 import PdfReader
    from PIL import Image
    import pytesseract
    from django.conf import settings
    from .models import Upload, Staff


    title= request.POST['title']
    file = request.FILES.get('file')
    if not file:
        return redirect('/myapp/upload_file/#abc')

    # Allowed file extensions
    allowed_extensions = [
        '.jpg', '.jpeg', '.png',
        '.pdf',
        '.doc', '.docx',
        '.xls', '.xlsx',
        '.csv'
    ]

    ext = os.path.splitext(file.name)[1].lower()

    if ext not in allowed_extensions:
        messages.error(request, "Unsupported File Type!")
        return redirect('/myapp/upload_file/#abc')

    # ===============================
    # 🔹 DUPLICATE CHECK (HASH)
    # ===============================
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    file_hash = hasher.hexdigest()
    file.seek(0)

    if Upload.objects.filter(hashvalue=file_hash).exists():
        messages.error(request, 'Duplicate File Detected!')
        return redirect('/myapp/upload_file/#abc')

    # ===============================
    # 🔹 SAVE FILE
    # ===============================
    fs = FileSystemStorage()
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + ext
    saved_name = fs.save(filename, file)


    full_path = os.path.join(settings.MEDIA_ROOT, saved_name)

    extracted_text = ""

    # ===============================
    # 🔹 EXTRACT CONTENT
    # ===============================

    # PDF
    if ext == ".pdf":
        reader = PdfReader(full_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

    # CSV
    elif ext == ".csv":
        with open(full_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                extracted_text += " | ".join(row) + "\n"

    # IMAGE (OCR)
    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(full_path)
        extracted_text = pytesseract.image_to_string(image)

    else:
        extracted_text = "Text extraction not implemented for this format."

    # ===============================
    # 🔹 SAVE TO DATABASE
    # ===============================
    staff = Staff.objects.get(USER_id=request.user.id)

    upload_obj = Upload.objects.create(
        document="/media/"+saved_name,
        Date=datetime.now(),
        STAFF=staff,
        hashvalue=file_hash,
        title=title
    )

    # ===============================
    # 🔹 SAVE TO JSON FILE (APPEND)
    # ===============================

    json_file_path = r"C:\AetherAI\AetherAI\media\uploaded_data.json"

    new_record = {
        "id": upload_obj.id,
        "date": str(upload_obj.Date),
        "staff": staff.id,
        "content": extracted_text
    }

    # If JSON exists → append
    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []

    data.append(new_record)

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # ======================================================
    # LOAD JSON
    # ======================================================
    print("Loading JSON...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)

    # ======================================================
    # HELPER FUNCTIONS
    # ======================================================
    def is_valid_document(doc):
        text = doc.get("content", "").strip()
        if len(text) < 100 or "Text extraction not implemented" in text:
            return False
        return True

    def chunk_legal_text(text, min_words=40):
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if len(p.split()) >= min_words]

    # ======================================================
    # CREATE NEW INDEX
    # ======================================================
    print("Creating FAISS index...")

    metadata = []
    processed_ids = set()
    all_chunks = []

    for doc in documents:
        if not is_valid_document(doc):
            continue

        chunks = chunk_legal_text(doc["content"])

        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({
                "doc_id": doc["id"],
                "date": doc.get("date", ""),
                "staff": doc.get("staff", ""),
                "text": chunk
            })

        processed_ids.add(doc["id"])

    print("Generating embeddings...")

    embeddings = model.encode(
        all_chunks,
        batch_size=128,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings / np.linalg.norm(
        embeddings, axis=1, keepdims=True
    )

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Save everything
    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    with open(PROCESSED_IDS_PATH, "wb") as f:
        pickle.dump(processed_ids, f)

    print("Index generation completed successfully.")

    messages.success(request, 'File Uploaded & Content Saved to JSON!')
    return redirect('/myapp/upload_file/#abc')

@login_required(login_url='/myapp/loginpage_get/')
def view_upload_file(request):
    data=Upload.objects.all().order_by('-id')
    return render(request, 'staff/view_uploadfile.html', {'data':data})


# def extract_content(request,id):
#     file=Upload.objects.get(id=id).document
#
#     return render(request,'staff/view_content.html',{'data'})

# @login_required(login_url='/myapp/loginpage_get/')
# def extract_content(request, id):
#     upload = Upload.objects.get(id=id)
#     file_path = upload.document  # example: /media/20260114191244.pdf
#
#     import os
#     from django.conf import settings
#
#     full_path = os.path.join(settings.BASE_DIR, file_path.lstrip('/'))
#
#     extracted_text = ""
#
#     # ===== PDF FILE =====
#     if file_path.lower().endswith('.pdf'):
#         from PyPDF2 import PdfReader
#         reader = PdfReader(full_path)
#         for page in reader.pages:
#             extracted_text += page.extract_text() + "\n"
#
#     # ===== CSV FILE =====
#     elif file_path.lower().endswith('.csv'):
#         import csv
#         with open(full_path, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 extracted_text += " | ".join(row) + "\n"
#
#     else:
#         extracted_text = "Unsupported file format"
#
#     return render(request, 'staff/view_content.html', {
#         'data': extracted_text,
#         # 'file': upload
#     })

# @login_required(login_url='/myapp/loginpage_get/')
# def extract_content(request, id):
#     upload = Upload.objects.get(id=id)
#     file_path = upload.document  # /media/20260114191244.pdf
#     print(file_path,"file path..................")
#
#     import os
#     from django.conf import settings
#
#     # Correct full file path
#     full_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(file_path))
#     print(full_path,"fuuuuullllll paaathhhh")
#
#     extracted_text = ""
#
#     # ===== PDF =====
#     if file_path.lower().endswith('.pdf'):
#         from PyPDF2 import PdfReader
#         reader = PdfReader(full_path)
#         for page in reader.pages:
#             text = page.extract_text()
#             if text:
#                 extracted_text += text + "\n"
#
#     # ===== CSV =====
#     elif file_path.lower().endswith('.csv'):
#         import csv
#         with open(full_path, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 extracted_text += " | ".join(row) + "\n"
#
#     else:
#         extracted_text = "Unsupported file format"
#
#     return render(request, 'staff/view_content.html', {
#         'data': extracted_text
#     })
#
#
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from transformers import pipeline
#
# # Load once (IMPORTANT for performance)
#
#
# @login_required(login_url='/myapp/loginpage_get/')
# def ask_question(request):
#     qa_pipeline = pipeline(
#         "question-answering",
#         model="distilbert-base-cased-distilled-squad"
#     )
#     context = request.session.get("document_text", "")
#     answer = ""
#
#     if request.method == "POST":
#         question = request.POST.get("question")
#
#         if question and context:
#             result = qa_pipeline(
#                 question=question,
#                 context=context[:4000]  # model limit safety
#             )
#             answer = result["answer"]
#
#     return render(request, 'staff/view_content.html', {
#         'answer': answer
#     })
#
#     # return render(request, "staff/qa_page.html", {
#     #     "data": context,
#     #     "answer": answer
#     # })


from transformers.pipelines import pipeline
from .models import Upload

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
import os, csv

from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@login_required(login_url='/myapp/loginpage_get/')
def extract_content(request, id):
    upload = Upload.objects.get(id=id)
    file_path = upload.document  # /media/filename.ext

    full_path = os.path.join(
        settings.MEDIA_ROOT,
        os.path.basename(file_path)
    )

    extracted_text = ""

    # -------- PDF --------
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(full_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

    # -------- CSV --------
    elif file_path.lower().endswith(".csv"):
        with open(full_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                extracted_text += " | ".join(row) + "\n"

    # -------- IMAGE (OCR) --------
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        image = Image.open(full_path)
        extracted_text = pytesseract.image_to_string(image)

    else:
        extracted_text = "Unsupported file format"

    # ✅ Store extracted text in session
    request.session["document_text"] = extracted_text

    return render(request, "staff/view_content.html", {
        "data": extracted_text
    })
@login_required(login_url='/myapp/loginpage_get/')
def ask_question(request):
    qa_pipeline = pipeline(
        "question-answering",
        model="distilbert-base-cased-distilled-squad"
    )

    context = request.session.get("document_text", "")
    answer = ""

    if request.method == "POST":
        question = request.POST.get("question")

        if question and context:
            result = qa_pipeline(
                question=question,
                context=context[:4000]
            )
            answer = result["answer"]

    return render(request, "staff/view_content.html", {
        "data": context,
        "answer": answer
    })



# user=User.objects.get(username="admin@gmail.com")
# user.set_password("123456")
# user.save()

def ask_doubt(request):
    return render(request,'staff/ask_doubt.html')



@csrf_exempt
def ask_question_post(request):
    question = request.POST.get("question")

    # ======================================================
    # SETTINGS
    # ======================================================
    INDEX_PATH = r"C:\AetherAI\AetherAI\myapp\legal_index.faiss"
    METADATA_PATH = r"C:\AetherAI\AetherAI\myapp\metadata.pkl"

    print("Loading FAISS index...")
    index = faiss.read_index(INDEX_PATH)

    print("Loading metadata...")
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    print("System Ready ✅")

    # ======================================================
    # SEMANTIC SEARCH FUNCTION
    # ======================================================
    def legal_search(query, top_k=5, min_score=0.50):
        """
        Strict semantic search
        - No keyword boost
        - Uses cosine similarity (IndexFlatIP with normalized vectors)
        - Filters weak results using threshold
        """

        # Encode query
        query_embedding = model.encode(
            [query],
            convert_to_numpy=True
        )

        # Normalize (important for cosine similarity)
        query_embedding = query_embedding / np.linalg.norm(
            query_embedding, axis=1, keepdims=True
        )

        # Search directly top_k only
        distances, indices = index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, idx in zip(distances[0], indices[0]):

            # Strict threshold filtering
            if score < min_score:
                continue

            if idx >= len(metadata):
                continue

            data = metadata[idx]

            results.append({
                "score": round(float(score), 4),
                "doc_id": data["doc_id"],
                "date": data["date"],
                "staff": data["staff"],
                "snippet": data["text"][:600]
            })

        return results
    # def legal_search(query, top_k=5):
    #
    #     query_embedding = model.encode([query])
    #     query_embedding = query_embedding / np.linalg.norm(query_embedding)
    #
    #     distances, indices = index.search(
    #         np.array(query_embedding),
    #         top_k * 3
    #     )
    #
    #     seen = set()
    #     results = []
    #
    #     for score, idx in zip(distances[0], indices[0]):
    #
    #         if idx >= len(metadata):
    #             continue
    #
    #         data = metadata[idx]
    #
    #         if data["text"] in seen:
    #             continue
    #
    #         seen.add(data["text"])
    #
    #         boost = 0.1 if query.lower() in data["text"].lower() else 0.0
    #
    #         results.append({
    #             "score": round(float(score + boost), 4),
    #             "doc_id": data["doc_id"],
    #             "date": data["date"],
    #             "staff": data["staff"],
    #             "snippet": data["text"][:600]
    #         })
    #
    #         if len(results) == top_k:
    #             break
    #
    #     return results

    # ======================================================
    # INTERACTIVE SEARCH
    # ======================================================
    print("\n⚖️ Legal Search Ready")
    print("Type 'exit' to stop.\n")

    # while True:
    query = question

    # if query.lower() == "exit":
    #     break

    results = legal_search(query)

    print("\nRESULTS:\n")
    k=set()
    for r in results:
        k.add(r["doc_id"])
        print("Score:", r["score"])
        print("Doc ID:", r["doc_id"])
        print("Date:", r["date"])
        print("Staff:", r["staff"])
        print("Snippet:\n", r["snippet"])
        print("=" * 80)

    data=Upload.objects.filter(id__in=k)

    return render(request, 'staff/ask_doubt.html',{'data':data})