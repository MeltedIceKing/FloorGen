from django import forms

class TwoExcelUploadForm(forms.Form):
    excel_file_1 = forms.FileField(label='Select Sessions by Finish Time File')
    excel_file_2 = forms.FileField(label='Select Sessions by Screen File')