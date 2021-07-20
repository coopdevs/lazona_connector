import base64
import os


class Delivery:
    pdf_folder = "pdf_barcodes"

    def __init__(self, data, vendor, req_body={}):
        self.data = data
        self.vendor = vendor
        self.req_body = req_body

    def to_dict(self):
        return {
            "barcode": self.data.get("codBarras", ""),
            "label": self.data.get("etiqueta", ""),
            "order_id": self.data.get("order_id", ""),
            "shipment_id": self.data.get("numPedido", ""),
            "message": self.data.get("mensaje", ""),
            "response": self.data.get("respuesta", "")
        }

    def _is_errored(self):
        return self.get_data_val("response") != "101"

    def print_pdf(self):
        content = base64.b64decode(self.get_data_val("label"))
        pdf_path = os.path.join(self.pdf_folder, f"{self.get_data_val('shipment_id')}.pdf")
        if not os.path.exists(pdf_path):
            pdf = open(pdf_path, "wb")
            pdf.write(content)
            pdf.close()

        return pdf_path

    def get_data_val(self, key):
        return self.to_dict()[key]
