from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange
from project import app

class RegistrationForm(FlaskForm):
    organization = StringField(label = "Organization")
    mid = StringField(label = "Merchant ID")
    username = StringField(label = 'Username', validators = [DataRequired(), Length(min=3, max=20)])
    email = StringField(label = 'Email', validators = [DataRequired(), Email()])
    password = PasswordField(label = 'Password', validators = [DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField(label = 'Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField(label = 'Create')
    
class ChangePasswordForm(FlaskForm):
    password = PasswordField(label = 'Password', validators = [DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField(label = 'Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField(label = 'Reset My Password')

class ForgotPasswordForm(FlaskForm):
    email = StringField(label = 'Please enter your registered email address. Our team will email you the instruction to reset instruction.', validators = [DataRequired(), Email()])
    submit = SubmitField(label = 'Reset')

class LoginForm(FlaskForm):
    email = StringField(label = 'Email', validators = [DataRequired(), Email()])
    password = PasswordField(label = 'Password', validators = [DataRequired(), Length(min=6, max=16)])
    submit = SubmitField(label = 'Login')

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

    def Load(self, filename):
        print(f"=== load: {{filename}} =====")
        
        path=app.config['UPLOAD_WE_TEST_DIR'] + "/" + filename
        print(path)
        
        with open(path) as file:
            for line in file:

                line = line.rstrip()
                if line == "":
                    continue
                
                array = line.split(',')
                if len(array) < 2:
                    continue
                
                array[0] = array[0].rstrip()
                array[1] = array[1].rstrip()
                
                if array[0] == "MPI_TRANS_TYPE":
                    self.MPI_TRANS_TYPE.data 	= array[1]
                elif array[0] == "MPI_MERC_ID":
                    self.MPI_MERC_ID.data 	= array[1]
                elif array[0] == "MPI_PAN":
                    self.MPI_PAN.data 	= array[1]
                elif array[0] == "MPI_PAN_EXP":
                    self.MPI_PAN_EXP.data 	= array[1]
                elif array[0] == "MPI_CVV2":
                    self.MPI_CVV2.data 	= array[1]
                elif array[0] == "MPI_CARD_HOLDER_NAME": 
                    self.MPI_CARD_HOLDER_NAME.data 	= array[1]
                elif array[0] == "MPI_PURCH_AMT":
                    self.MPI_PURCH_AMT.data 	= array[1]
                elif array[0] == "MPI_PURCH_CURR":
                    self.MPI_PURCH_CURR.data 	= array[1]
                elif array[0] == "MPI_TRXN_ID": 
                    self.MPI_TRXN_ID.data 	= array[1]
                elif array[0] == "MPI_ORI_TRXN_ID":
                    self.MPI_ORI_TRXN_ID.data 	= array[1]
                elif array[0] == "MPI_PURCH_DATE":
                    self.MPI_PURCH_DATE.data 	= array[1]
                elif array[0] == "MPI_ADDR_MATCH":
                    self.MPI_ADDR_MATCH.data 	= array[1]
                elif array[0] == "MPI_BILL_ADDR_CITY":
                    self.MPI_BILL_ADDR_CITY.data 	= array[1]
                elif array[0] == "MPI_BILL_ADDR_STATE": 
                    self.MPI_BILL_ADDR_STATE.data 	= array[1]
                elif array[0] == "MPI_BILL_ADDR_CNTRY":
                    self.MPI_BILL_ADDR_CNTRY.data 	= array[1]
                elif array[0] == "MPI_PURCH_CURR":
                    self.MPI_PURCH_CURR.data 	= array[1]
                elif array[0] == "MPI_BILL_ADDR_POSTCODE":
                    self.MPI_BILL_ADDR_POSTCODE.data 	= array[1]  
                elif array[0] == "MPI_BILL_ADDR_LINE1":
                    self.MPI_BILL_ADDR_LINE1.data 	= array[1]
                elif array[0] == "MPI_BILL_ADDR_LINE2":
                    self.MPI_BILL_ADDR_LINE2.data 	= array[1]
                elif array[0] == "MPI_BILL_ADDR_LINE3":
                    self.MPI_BILL_ADDR_LINE3.data 	= array[1]
                elif array[0] == "MPI_SHIP_ADDR_CITY":
                    self.MPI_SHIP_ADDR_CITY.data 	= array[1]
                elif array[0] == "MPI_SHIP_ADDR_STATE": 
                    self.MPI_SHIP_ADDR_STATE.data 	= array[1]
                elif array[0] == "MPI_SHIP_ADDR_CNTRY":
                    self.MPI_SHIP_ADDR_CNTRY.data 	= array[1]
                elif array[0] == "MPI_SHIP_ADDR_POSTCODE":
                    self.MPI_SHIP_ADDR_POSTCODE.data 	= array[1]
                elif array[0] == "MPI_SHIP_ADDR_LINE1":  
                    self.MPI_SHIP_ADDR_LINE1.data 	= array[1]
                elif array[0] == "MPI_SHIP_ADDR_LINE2":
                    self.MPI_SHIP_ADDR_LINE2.data 	= array[1]
                elif array[0] == "MPI_SHIP_ADDR_LINE3":
                    self.MPI_SHIP_ADDR_LINE3.data 	= array[1]
                elif array[0] == "MPI_EMAIL":
                    self.MPI_EMAIL.data 	= array[1]
                elif array[0] == "MPI_HOME_PHONE_CC":
                    self.MPI_HOME_PHONE_CC.data 	= array[1]
                elif array[0] == "MPI_HOME_PHONE": 
                    self.MPI_HOME_PHONE.data 	= array[1]
                elif array[0] == "MPI_MOBILE_PHONE_CC":
                    self.MPI_MOBILE_PHONE_CC.data 	= array[1]
                elif array[0] == "MPI_MOBILE_PHONE":
                    self.MPI_MOBILE_PHONE.data 	= array[1]
                elif array[0] == "MPI_WORK_PHONE_CC":  
                    self.MPI_WORK_PHONE_CC.data 	= array[1]
                elif array[0] == "MPI_WORK_PHONE":
                    self.MPI_WORK_PHONE.data 	= array[1]
                elif array[0] == "MPI_ADDITIONAL_INFO_IND":
                    self.MPI_ADDITIONAL_INFO_IND.data 	= array[1]
                elif array[0] == "MPI_RECURRING_FREQUENCY":
                    self.MPI_RECURR_FREQ.data 	= array[1]
                elif array[0] == 'MPI_RECURR_FREQ':
                    self.MPI_RECURR_FREQ.data 	= array[1]
                elif array[0] == "MPI_RECURRING_EXPIRY": 
                    self.MPI_RECURR_EXPIRY.data 	= array[1]
                elif array[0] == 'MPI_RECURR_EXPIRY':
                    self.MPI_RECURR_EXPIRY.data 	= array[1]
                elif array[0] == "MPI_PURCHASE_INSTAL_DATA":
                    self.MPI_RECURR_MAX_CNT.data 	= array[1]
                elif array[0] == 'MPI_RECURR_MAX_CNT':
                    self.MPI_RECURR_MAX_CNT.data 	= array[1]
                elif array[0] == "MPI_RECURRING_MAX_PURCHASE_AMOUNT":
                    self.MPI_RECURR_MAX_AMT.data 	= array[1]
                elif array[0] == 'MPI_RECURR_MAX_AMT':
                    self.MPI_RECURR_MAX_AMT.data 	= array[1]
                elif array[0] == "MPI_RECURRING_TOTAL_PURCHASE_AMOUNT":
                    self.MPI_RECURR_MAX_TOTAL.data 	= array[1]  
                elif array[0] == 'MPI_RECURR_MAX_TOTAL':
                    self.MPI_RECURR_MAX_TOTAL.data = array[1]

class RedirectUrlProxyForm(FlaskForm):
    key = StringField(label = "Key - Transaction ID Prefix (2 characters)")
    mid = StringField(label = "Merchant ID")
    url = StringField(label = "Redirection URL")
    status_url = StringField(label = "Status URL")
    enable = SelectField(label = "Indicator (Y-enable/N-disable)", 
        choices = [('Y'),('N')])
    add = SubmitField(label = 'Add New Redirection URL')        
 
class LiveEnvForm(FlaskForm):
     mid = StringField(label = "Production MID", render_kw={"placeholder": "Production MID", 'readonly': True})
     mProxyKey = StringField(label = "Proxy Key", render_kw={"placeholder": "TXID Prefix (2 chars)"})
     #url = StringField(label = "Redirection URL", render_kw={"placeholder": "Event Webhook", "cols" : 33})
     url = StringField(label = "Redirection URL", validators = [DataRequired()])
     #status_url = StringField(label = "Status Webhook", render_kw={"placeholder": "Status Webhook", "cols" : 33})
     status_url = StringField(label = "Status Webhook")
     rsa_key = FileField(label = "RSA Key (one time setup):", render_kw={"placeholder": "RSA Key (one time setup)", "type" : "file"})
     submit = SubmitField(label = "Update")
 
class MacValidateForm(FlaskForm): 

    public_rsa_key = TextAreaField(label = "Public RSA Key:", render_kw={"placeholder": "Public RSA Key"})
    public_rsa_key = TextAreaField(label = "Private RSA Key:", render_kw={"placeholder": "Private RSA Key",})
    data = TextAreaField(label = "Data", render_kw={"placeholder": "Paste your data here"})
    mac  = TextAreaField(label = "MAC Signature:", render_kw={"placeholder": "Paste your MAC signature here"})
    verify = SubmitField(label = "Verify the MAC Signature")
    sign_mac = SubmitField(label = ">> Please generate me a MAC Signature")

 
 
