#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import RadioField, BooleanField, FloatField
from wtforms.validators import InputRequired, Optional

class CColor(Form):
  resol = RadioField(u'Rozlišení', choices=[('high', u'Velké'), ('low', u'Malé')], validators=[Optional()])
  uloz = BooleanField(u'Uložit', validators=[Optional()])
  hodnot = FloatField(u'Jas', validators=[InputRequired()])

