import base64
import os

# TODO: convert this class into Django Model in order to link Koiki's shipping,
# with WC purchase and PDF


class Delivery:
    pdf_folder = "pdf_barcodes"

    def __init__(self, data, vendor, req_body={}):
        self.data = data
        self.vendor = vendor
        self.req_body = req_body
        self.shipment_id = data["numPedido"]
        self.order_id = data["order_id"]

    def to_dict(self):
        return {
            "number": self.data["numPedido"],
            "barcode": self.data["codBarras"],
            "label": self.data["etiqueta"],
            "order_id": self.data["order_id"]
        }

    def _is_errored(self):
        return self.data.get("respuesta", "") != "101"

    def print_pdf(self):
        content = base64.b64decode(self.data["etiqueta"])
        pdf_path = os.path.join(self.pdf_folder, f"{self.shipment_id}.pdf")
        if not os.path.exists(pdf_path):
            pdf = open(pdf_path, "wb")
            pdf.write(content)
            pdf.close()

        return pdf_path
