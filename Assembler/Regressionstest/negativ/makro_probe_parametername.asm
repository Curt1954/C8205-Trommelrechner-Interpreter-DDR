; makro_probe_parametername: PROBE ist ein festes Wort und als Parametername verboten, auch klein geschrieben (Doku 4.26)
M1:     MACRO probe
        dw      $probe
        MEND
        start
        M1      1
        end
