import os

from multidb.pinning import use_master
from rest_framework.authentication import BasicAuthentication
from rest_framework.settings import api_settings
from rest_framework.viewsets import ReadOnlyModelViewSet

from onadata.apps.viewer.models.export import Export
from onadata.libs.renderers import renderers
from onadata.libs.serializers.export_serializer import ExportSerializer
from onadata.libs.authentication import (
    DigestAuthentication,
    TempTokenAuthentication,
    TempTokenURLParameterAuthentication)
from onadata.libs.utils.logger_tools import response_with_mimetype_and_name
from onadata.libs import filters


class ExportViewSet(ReadOnlyModelViewSet):
    authentication_classes = (DigestAuthentication,
                              TempTokenAuthentication,
                              TempTokenURLParameterAuthentication,
                              BasicAuthentication)
    queryset = Export.objects.filter()
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [
        renderers.CSVRenderer,
        renderers.CSVZIPRenderer,
        renderers.KMLRenderer,
        renderers.OSMExportRenderer,
        renderers.SAVZIPRenderer,
        renderers.XLSRenderer,
        renderers.XLSXRenderer,
        renderers.ZipRenderer
    ]
    serializer_class = ExportSerializer
    filter_backends = (filters.ExportFilter,)

    @use_master
    def retrieve(self, request, *args, **kwargs):
        export = self.get_object()
        filename, extension = os.path.splitext(export.filename)
        extension = extension[1:]

        return response_with_mimetype_and_name(
            Export.EXPORT_MIMES[extension],
            filename,
            extension=extension,
            file_path=export.filepath,
            show_date=False)
