from django.forms import ModelForm
import vhcm.models.reference_document as document_model


class DocumentEditForm(ModelForm):
    class Meta:
        # write the name of models for which the form is made
        model = document_model.RefercenceDocument
        # Custom fields
        fields = [document_model.ID, document_model.NAME, document_model.LINK, document_model.AUTHOR]


class DocumentAddForm(ModelForm):
    class Meta:
        # write the name of models for which the form is made
        model = document_model.RefercenceDocument
        # Custom fields
        fields = [document_model.NAME, document_model.LINK, document_model.AUTHOR]
