from django.forms.widgets import Input, MultiWidget, FileInput
from django.core.validators import EMPTY_VALUES
from django.utils.safestring import mark_safe
from django.core.files.uploadedfile import UploadedFile

try:
    unicode
except NameError:
    unicode = str

__all__ = ['RadioInput', 'URLInput', 'MutuallyExclusiveRadioWidget',
           'FileOrURLWidget']


class RadioInput(Input):
    input_type = 'radio'


# for compatiblity with older Django verisons
class URLInput(Input):
    input_type = 'url'


class MutuallyExclusiveRadioWidget(MultiWidget):
    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        nonempty_widget = 0
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            else:
                if widget_value not in EMPTY_VALUES:
                    nonempty_widget = i
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(widget.render(
                name + '_%s' % i, widget_value, final_attrs))
        return mark_safe(unicode(
            self.format_output(nonempty_widget, name, output)))

    def format_output(self, nonempty_widget, name, rendered_widgets):
        radio_widgets = [RadioInput().render(
            name + '_radio', '', {})] * len(rendered_widgets)
        if nonempty_widget is not None:
            radio_widgets[nonempty_widget] = RadioInput().render(
                name + '_radio', '', {'checked': ''})
        tpl = """
<span id="{name}_container" class="mutually-exclusive-widget"
    style="display:inline-block">
    {widgets}
</span>"""

        return tpl.format(name=name, widgets='<br>'.join(
            '<span>{0}</span>'.format(x + y)
            for x, y in zip(radio_widgets, rendered_widgets)))

    def decompress(self, value):
        """
        If initialized with single compressed value we don't know what to do.
        just so it doesn't 'splode, return empty list of right length
        """
        return [''] * len(self.widgets)

    class Media:
        js = ('mutually_exclusive_widget.js',)


class FileOrURLWidget(MutuallyExclusiveRadioWidget):
    def __init__(self, attrs=None):
        url_attrs = dict(placeholder='Enter URL')
        if attrs is not None:
            url_attrs.update(attrs)
        widgets = (FileInput(attrs=attrs), URLInput(attrs=url_attrs))
        super(FileOrURLWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, UploadedFile):
            return [value, '']
        else:
            return ['', value]

    def value_from_datadict(self, data, files, name):
        # We want to accept a value via the name itself to support use in
        # tastypie resources.
        if name in data:
            return self.decompress(data[name])
        elif name in files:
            return self.decompress(files[name])
        else:
            return super(FileOrURLWidget, self).value_from_datadict(
                data, files, name)
