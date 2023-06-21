
from typing import List
from domain.entities.foment_instrument import FomentInstrument
from domain.repositories.foment_instrument_interface import IFomentInstrumentRepository
from helpers.send_email import send_email
from helpers.get_html import get_html
import requests
# Conexão com o db
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class FomentInstrumentRepositoryGSheet(IFomentInstrumentRepository):
    def __init__(self) -> None:
        super().__init__()
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', scope)
        gc = gspread.authorize(credentials)
        wks = gc.open_by_key('1lCDzonMnRdp27YATOShnepldzHSuEGqIZgvt8Lyy3es')
        self.control_sheet = wks.worksheet("Controle")
        self.control_sheet_values = self.control_sheet.get_all_values()

    def scan_all_urls(self):
        foment_instruments = self.get_all_foment_instruments()
        foment_instruments_changed = []
        for foment_instrument in foment_instruments:
            if foment_instrument.edital_url != "":
                actual_page = get_html(requests.get(
                    foment_instrument.edital_url))
                if (foment_instrument.edital_html != actual_page):
                    foment_instruments_changed.append(
                        foment_instrument.edital_url)
                # save new html
                new_foment_instrument = foment_instrument
                new_foment_instrument.edital_html = actual_page
                self.update_foment_instrument(
                    fomentInstrumentCode=foment_instrument.code,
                    newState=new_foment_instrument
                )
            if foment_instrument.news_url != "":
                actual_page = get_html(
                    requests.get(foment_instrument.news_url))
                if (foment_instrument.news_html != actual_page):
                    foment_instruments_changed.append(
                        foment_instrument.news_url)
                # save new html
                new_foment_instrument = foment_instrument
                new_foment_instrument.news_html = actual_page
                self.update_foment_instrument(
                    fomentInstrumentCode=foment_instrument.code,
                    newState=new_foment_instrument
                )

        email_body = f"""
                <h1>Alerta! Houve uma mudança nos seguintes sites:</h1>
                <div>
                    <ul>
                        {" ".join([f'<li><a href="{url}">{url}<a></li>' for url in foment_instruments_changed])}
                    </ul>
                </div>
            """

        send_email(subject="Alerta! Mundaça em sites de fomento.",
                   body=email_body)

        return True

    def get_all_foment_instruments(self) -> List[FomentInstrument]:
        all_foment_instruments = []
        for foment_instrument in self.control_sheet_values:
            all_foment_instruments.append(FomentInstrument(
                code=foment_instrument[0],
                acronym=foment_instrument[1],
                name=foment_instrument[2],
                foment_type=foment_instrument[3],
                edital_url=foment_instrument[4],
                edital_html=foment_instrument[5],
                news_url=foment_instrument[6],
                news_html=foment_instrument[7]
            )
            )
        return all_foment_instruments

    def get_foment_instrument_by_code(self, fomentInstrumentCode: str) -> FomentInstrument:
        for foment_instrument in self.control_sheet_values:
            if foment_instrument.code == fomentInstrumentCode:
                return FomentInstrument(
                    code=foment_instrument[0],
                    acronym=foment_instrument[1],
                    name=foment_instrument[2],
                    foment_type=foment_instrument[3],
                    edital_url=foment_instrument[4],
                    edital_html=foment_instrument[5],
                    news_url=foment_instrument[6],
                    news_html=foment_instrument[7]
                )

        return None

    def update_foment_instrument(self, fomentInstrumentCode: str, newState: FomentInstrument) -> FomentInstrument:
        row_number = 0
        for foment_instrument in self.control_sheet_values:
            row_number += 1
            if foment_instrument.code == fomentInstrumentCode:
                self.control_sheet.update_cell(
                    row_number, 2, foment_instrument.acronym)
                self.control_sheet.update_cell(
                    row_number, 3, foment_instrument.name)
                self.control_sheet.update_cell(
                    row_number, 4, foment_instrument.foment_type)
                self.control_sheet.update_cell(
                    row_number, 5, foment_instrument.edital_url)
                self.control_sheet.update_cell(
                    row_number, 6, foment_instrument.edital_html)
                self.control_sheet.update_cell(
                    row_number, 7, foment_instrument.news_url)
                self.control_sheet.update_cell(
                    row_number, 8, foment_instrument.new_html)

        return newState

    # To Do
    # @abstractmethod
    # def create_foment_instrument(self, fomentInstrument: FomentInstrument) -> FomentInstrument:
    #     pass

    # @abstractmethod
    # def delete_foment_instrument(self, fomentInstrumentCode: str) -> bool:
    #     pass
