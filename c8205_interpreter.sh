file="$1"

if [ -z "$file" ]; then
    echo "Test-Datei fehlt."
    exit 1
fi

# Dateiname ohne Pfad, Endung durch .log ersetzen
prot_file="$(basename "$file")"
prot_file="${prot_file%.*}.log"

python3 c8205_interp.py --out "Protokolle/$prot_file" "$file"

