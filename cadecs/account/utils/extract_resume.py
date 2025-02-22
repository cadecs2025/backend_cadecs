import pdfplumber
import spacy
import re



class ExtractData:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract_text_from_pdf(self,pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    def extract_name_from_pdf(self,text):
        doc = self.nlp(text)
        keywords = ['email', 'Ph. No', 'ph no', 'phone no', 'mobile', 'mobile no',
                    'skype', 'linkedin', 'phone number', 'mobile number']
        
        pattern = r'\b(' + '|'.join(re.escape(word) for word in keywords) + r')\b'

        resume_lst = ['resume','cv','Curriculum vitae']

        # Extract name (assuming the first entity is the name)
        name = None
        for ent in doc.ents:
            print("ent---",ent)
            resume_status = all(sub in ent.text for sub in resume_lst)
            if not resume_status:
                if '\n' in ent.text:
                    name_lst = ent.text.split('\n')
                    name=name_lst[0]
                elif ',' in ent.text:
                    name_lst = ent.text.split('\n')
                    name=name_lst[0]
                elif ent.label_ == "PERSON":
                    name = ent.text
                else:
                    name = ent.text
                break

        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        name_lst = name.split()
        middle_name = None
        last_name = None
        first_name = None
        if len(name_lst)==2:
            first_name = name_lst[0]
            last_name = name_lst[1]
        elif len(name_lst)>2:
            first_name = name_lst[0]
            middle_name = name_lst[1]
            last_name = name_lst[2]
        else:
            first_name = name

        return first_name, middle_name, last_name

    def extract_phone_from_pdf(self,text):
        phone = re.findall(r"\+?\d[\d -]{8,}\d", text)
        phone = list(set(phone))

        return phone
    
    def extract_email_from_pdf(self,text):
        email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        return email
    
    def extract_region_from_pdf(self,text):
        city= None
        state = None
        country = None
        return city, state, country
    
    def extract_address_from_pdf(self,text):
        doc = self.nlp(text)
        address_pattern = re.compile(r'\d+[\s\w.,-]+(?:\s[A-Za-z]+){1,3}\s\d{5}(?:\s[\w\s]+)?')
        addresses = []
        for ent in doc.ents:
            matches = address_pattern.findall(ent.text)            
            if matches:
                addresses.extend(matches) 
        address = " ".join(addresses)
        zipcode= None        
        return address,zipcode   
    
    
    def extract_information(self,pdf_path):  

        text = self.extract_text_from_pdf(pdf_path)

        # print(f"text: {text}",flush=True)
        first_name, middle_name, last_name = self.extract_name_from_pdf(text)
        email = self.extract_email_from_pdf(text)
        phone = self.extract_phone_from_pdf(text)

        # print(f"phone: {phone}",flush=True)
        addresses,zipcode = self.extract_address_from_pdf(text)
        city, state, country = self.extract_region_from_pdf(text)


        return {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "email": email[0] if email else None,
            "phone": phone[0] if phone else None,
            "alt_phone": phone[1] if len(phone)>=2 else None,
            "address": addresses,
            "city": city,
            "state": state,
            "country": country,
            "zip_code": zipcode,

        }