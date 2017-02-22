#!/usr/bin/python
# -*- coding: utf-8 -*-


#---------------------------------------------------
from flask import render_template, request, Response
from app import app
from forms import CColor
import picamera, cv2, os
from io import BytesIO
import numpy as np
import datetime


def sidebar(sd):
    """ Zobrazení bočního panelu. """
    return render_template('sidebar.html', side_bar=sd)

def header(hd):
    """ Zobrazení záhlaví """
    return render_template('header.html', hdr=hd)

def fnGetResol(res):
   """ Nastavení rozlišení """
   if res == 'high': 
     return (2592, 1944)
   elif res == 'low':
     return (1024, 768)
   else:
     return (1320, 990)

def fnGetFileName(base):
  """ Vrátí jméno souboru """
  fname = base
  fname = fname + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")+".jpg"
  return fname

@app.route('/')
@app.route('/index')
def index():
    """ Hlavní stránka """
    header('my header')
    return render_template('base.html', title=u'Digitální mikroskop')

@app.route('/tmpjpg1/<string:resol>/<string:uloz>')           
def normal(resol, uloz):  
    """ Sejmutí barevného obrazu """                           
    my_stream = BytesIO()                                     #
    with picamera.PiCamera() as camera:                       #
        camera.resolution = fnGetResol(resol)                 #
        camera.capture(my_stream, format='jpeg')              #
        my_stream.seek(0)                                     #
    if uloz == 'True':                                        #
      with open(fnGetFileName('normal'), 'wb') as f:          #
        f.write(my_stream.getvalue())                         #
    return Response(my_stream.read(), mimetype='image/jpeg')  #
    

@app.route('/tmpjpg2/<string:resol>/<string:uloz>')
def sedy(resol, uloz):    
    """ Sejmutí obrazu ve stupních šedi """
    my_stream = BytesIO()   
    with picamera.PiCamera() as camera:
        camera.resolution = fnGetResol(resol)
        camera.capture(my_stream, format='jpeg')
        nparr = np.fromstring(my_stream.getvalue(), np.uint8)
        foto = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
        sedyobr = cv2.cvtColor(foto, cv2.COLOR_BGR2GRAY)
        r, sedyobrb = cv2.imencode(".jpeg", sedyobr)
    if uloz == 'True':
       with open(fnGetFileName('sedy'), 'wb') as f:
           f.write(sedyobrb)
    return Response(bytearray(sedyobrb), mimetype='image/jpeg')
   
@app.route('/tmpjpg3/<string:resol>/<string:uloz>')
def prah(resol, uloz): 
    """ Sejmutí obrazu a jeho vyprahování """   
    my_stream = BytesIO()   
    with picamera.PiCamera() as camera:
        camera.resolution = fnGetResol(resol)
        camera.capture(my_stream, format='jpeg')
        nparr = np.fromstring(my_stream.getvalue(), np.uint8)
        foto = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        prah = cv2.adaptiveThreshold(foto, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)  
        r, prahb = cv2.imencode(".jpeg", prah)
    if uloz == 'True':
       with open(fnGetFileName('prah'), 'wb') as f:
           f.write(prahb)
        #cv2.imwrite(sfoto, sedyobr)
    return Response(bytearray(prahb), mimetype='image/jpeg')


@app.route('/tmpjpg4/<string:resol>/<string:uloz>/<float:hodnot>')
def jasny(resol, uloz, hodnot):  
    """ Sejmutí obrazu a úprava jasu """  
    def adjust_gamma(image, gamma=1.0):
       """ Nastavení gamy """
       # build a lookup table mapping the pixel values [0, 255] to
       # their adjusted gamma values
       invGamma = 1.0 / gamma
       table = np.array([((i / 255.0) ** invGamma) * 255
          for i in np.arange(0, 256)]).astype("uint8")
  
       # apply gamma correction using the lookup table
       return cv2.LUT(image, table)

    my_stream = BytesIO()   
    with picamera.PiCamera() as camera:
        camera.resolution = fnGetResol(resol)
        camera.capture(my_stream, format='jpeg')
        nparr = np.fromstring(my_stream.getvalue(), np.uint8)
        foto = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
        jasny = adjust_gamma(foto, hodnot)

        r, jasnyb = cv2.imencode(".jpeg", jasny)
    if uloz == 'True':
       with open(fnGetFileName('jas'), 'wb') as f:
           f.write(jasnyb)
        #cv2.imwrite(sfoto, sedyobr)
    return Response(bytearray(jasnyb), mimetype='image/jpeg')



@app.route('/fun/<int:funid>', methods=['GET', 'POST'])
def fun(funid):
    """ Vykreslení uživatelského rozhraní """
    form = CColor()
    res = 'unknown'
    if form.resol.data != 'None':
      res = form.resol.data
    uloz = form.uloz.data
    hodnot = form.hodnot.data
    if hodnot == None:
      hodnot = 1.5
    if  funid ==1: 
       txt = u"Nezpracovaný barevný snímek"
    elif  funid ==2: 
       txt = u"Šedý snímek"
    elif  funid ==3: 
       txt = u"Prahovaný snímek"
    elif  funid ==4: 
       txt = u"Snímek se zvýšeným jasem"
    return render_template('fun.html',  txt=txt, funid=funid, form=form, res=res, uloz=uloz, hodnot=hodnot)


