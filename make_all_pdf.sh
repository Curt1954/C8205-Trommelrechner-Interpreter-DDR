arr=(
  build_testhandbuch.py
  erzeuge_assemblerdokumentation_pdf.py
  erzeuge_bedienpult_peripherie_pdf.py
  erzeuge_bedienungsanleitung_pdf.py
  erzeuge_bis_pdf.py
  erzeuge_durchfuehrung_pdf.py
  erzeuge_einstieg_pdf.py
  erzeuge_einzelbefehlsliste_pdf.py
  erzeuge_gestaltungsrichtlinie_pdf.py
  erzeuge_knoten_pdfs.py
  erzeuge_knotentabellen_pdf.py
  erzeuge_kodetabellen_pdf.py
  erzeuge_lochstreifen_hilfsprogramme_pdf.py
  erzeuge_projektstruktur_pdf.py
  erzeuge_projektueberblick_pdf.py
  erzeuge_rechnerbeschreibung_pdf.py
  erzeuge_testuebersicht_pdf.py
)

for dat in "${arr[@]}"; do
  ./make_pdf.sh "$dat"
done
