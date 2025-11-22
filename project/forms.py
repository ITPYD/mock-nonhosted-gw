from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange
from project import app


class MpiForm(FlaskForm):
    MPI_TRANS_TYPE = SelectField(label = "Select Transaction Type", 
        choices = [('SALES'),('VSALES'),('REFUND'),('PRERECURR'),('INITRECURR'),
        ('RECURR'),('INITINSTL'),('INSTL'),('TERMINATE'),('PREAUTH'),('SALESCOMPL')], 
        validators =[DataRequired()])
    #MPI_TRANS_TYPE = StringField(label = "Transaction Type")
    MPI_MERC_ID = StringField(label = "Merchant ID")
    MPI_PAN = StringField(label = "Card Number", validators = [DataRequired(), Length(min=16,max=16)], render_kw={"placeholder": "Card Number"})
    MPI_PAN_EXP = StringField(label = "Expiry Date (yymm)", validators = [DataRequired(), Length(min=4,max=4)], render_kw={"placeholder": "YYMM"})
    MPI_CVV2 = StringField(label = "CVV2", validators = [DataRequired(), Length(min=3,max=54)], render_kw={"placeholder": "CVV"})
    MPI_CARD_HOLDER_NAME = StringField(label = "Card Holder Name", validators = [DataRequired(), Length(min=3,max=54)], render_kw={"placeholder": "Card Holder Name"})
    MPI_PURCH_AMT = StringField(label = "Amount", validators = [DataRequired(), NumberRange(min=0.00, max=1000000.00)])
    MPI_PURCH_CURR = StringField(label = "Purchase Currency")
    MPI_TRXN_ID = StringField(label = "Transaction ID")
    MPI_PURCH_DATE = StringField(label = "Purchase Date")
    MPI_MAC = StringField(label = "MAC")
    MPI_ADDR_MATCH = StringField(label = "Address Match")
    MPI_ORI_TRXN_ID = StringField(label = "Original Transaction ID")
    MPI_BILL_ADDR_CITY = StringField(label = "Billing Address")
    MPI_BILL_ADDR_STATE = StringField(label = "Billing Address State")
    MPI_BILL_ADDR_CNTRY = StringField(label = "Billing Address Country")
    MPI_BILL_ADDR_POSTCODE = StringField(label = "Billing Address Postcode")
    MPI_BILL_ADDR_LINE1 = StringField(label = "Billing Address")
    MPI_BILL_ADDR_LINE2 = StringField(label = "Billing Address")
    MPI_BILL_ADDR_LINE3 = StringField(label = "Billing Address")
    MPI_SHIP_ADDR_CITY = StringField(label = "Billing Address City")
    MPI_SHIP_ADDR_STATE = StringField(label = "Billing Address State")
    MPI_SHIP_ADDR_CNTRY = StringField(label = "Billing Address Country")
    MPI_SHIP_ADDR_POSTCODE = StringField(label = "Shipping Address Postcode")
    MPI_SHIP_ADDR_LINE1 = StringField(label = "Shipping Address")
    MPI_SHIP_ADDR_LINE2 = StringField(label = "Shipping Address")
    MPI_SHIP_ADDR_LINE3 = StringField(label = "Shipping Address")
    MPI_EMAIL = StringField(label = "Email")
    MPI_HOME_PHONE = StringField(label = "Home Phone")
    MPI_HOME_PHONE_CC = StringField(label = "Home Phine Cc")
    MPI_WORK_PHONE = StringField(label = "Office Phone")
    MPI_WORK_PHONE_CC = StringField(label = "Office Phone CC")
    MPI_MOBILE_PHONE = StringField(label = "Mobile Phone")
    MPI_MOBILE_PHONE_CC = StringField(label = "Mobile Number CC")
    MPI_RESPONSE_TYPE = SelectField(label = "Response Type", 
        choices = [(''),('JSON'),('STRING'),('HTML')])
    MPI_ADDITIONAL_INFO_IND = SelectField(label = "Additional Information Indicator", 
        choices = [(''),('Y'),('N')])
    MPI_RECURR_FREQ = StringField(label = "Recurring Frequency")
    MPI_RECURR_EXPIRY = StringField(label = "Recurring Expiry Date (yyyymmdd)")
    MPI_RECURR_MAX_CNT = StringField(label = "Recurring Max Count")
    MPI_RECURR_MAX_AMT = StringField(label = "Recurring Max Single Purchase Amount")
    MPI_RECURR_MAX_TOTAL = StringField(label = "Recurring Max Total Purchase Amount")


class MacValidateForm(FlaskForm): 

    public_rsa_key = TextAreaField(label = "Public RSA Key:", render_kw={"placeholder": "Public RSA Key"})
    public_rsa_key = TextAreaField(label = "Private RSA Key:", render_kw={"placeholder": "Private RSA Key",})
    data = TextAreaField(label = "Data", render_kw={"placeholder": "Paste your data here"})
    mac  = TextAreaField(label = "MAC Signature:", render_kw={"placeholder": "Paste your MAC signature here"})
    verify = SubmitField(label = "Verify the MAC Signature")
    sign_mac = SubmitField(label = ">> Please generate me a MAC Signature")

 
 
