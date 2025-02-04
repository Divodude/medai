from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from modeloutputs import generate
import wikipedia
from django.contrib.auth import authenticate,login
from start.models import conversation
from cnnmodel import check
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import numpy as np
import io
from django.views.decorators.csrf import csrf_exempt
from start.models import conversation
from keras.models import load_model
from cell import *
model = load_model('mymodel.h5')

import cv2
import numpy as np


# Create your views here.
def home(request):
    if request.method=="POST":
        text=request.POST.get("input")
        
       
       
        result,_=generate(text)
       # x=wikipedia.summary(result, sentences=1)

        context={"output":result,"web":"","conversation":conversation.objects.filter(user=request.user)}
        conversation.objects.update_or_create(prompt=text,responde=result,user=request.user)
        return render(request,"index.html",context)
    
    return render(request,"index.html",context={"user":request.user,"conversation":conversation.objects.filter(user= request.user)})


def auth(reuqest):
    
    if reuqest.method=='POST':
        email=reuqest.POST.get("email")
        password=reuqest.POST.get("password")

        try:
            user=User.objects.get(username=email)
        except:
            HttpResponse("error 404")
        user=authenticate(reuqest,username=email,password=password)
        if user is not None:
            
            login(reuqest,user)
            return redirect("home")
        else:
            HttpResponse("incorrect credentials")
        
    return render(reuqest,"next.html")




@csrf_exempt
def report_check(request):
    if request.method == 'POST':
        img_file = request.FILES.get("img") 
        if img_file:
            img = Image.open(img_file)  
            img_array = np.array(img)
            
            y = check(img_array)
            return render(request,'mri.html',{"prob":y})
        else:
            return HttpResponse("No image file provided", status=400)
    return render(request,'mri.html')


@csrf_exempt
def cell(request):
    if request.method == 'POST':
        img_file = request.FILES.get("img")
        if img_file:
            img = Image.open(img_file)
            img_array = np.array(img)
         
            if img_array.shape[-1] == 3: 
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            y = gen_giv(img_array)  
            cv2.imwrite("static/img.png", y)
            return render(request, 'cell.html', {"img": "static/img.png"})
        else:
            return HttpResponse("img")
    return render(request, "cell.html")









    