from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)

def fliplr(arr):
    return np.fliplr(arr)

def combvec(*args):
    return np.array(np.meshgrid(*args, indexing='ij')).T.reshape(-1, len(args))

def calculate_output(V):
    # Erstellung der  verschiedenen Kombinationen beim Dart 
    # Dafür Erstellung Matritzen welche Kombinationen enthalten, da mit einem Doppel oder 50 das Spiel beendet werden muss stellt die 
    # 3te Reihe immer ein Doppel oder Bull dar. Wenn ein Triple und Single benötigt wird zuerst auf das Triple gezieht
    # In gewissen Konstellationen kann der Wurf auf das Bullseye sinnvoll sein da im Falle einer Knappen Verfehlung 25 Punkte immer noch hoeher sind als das höchste Doppel (20)
    #Triple erst ab 21 (Triple 7) da alle Zahlen kleiner als 21 auch über die Single gespielt werden kann
    #Daraus final ergeben sich folgende Kombinationen
    
    #S1 enhält alle Triple Single Doppel Kombinationen
    #S2 enhält alle Double Double Double Kombinationen
    #S3 enhält alle Double Single Double Kombinationen
    #S4 enhält alle Triple Single Double Kombinationen
    #S5 enhält alle Triple Triple Double Kombinationen
    #S6 enhält alle Bullseye Single Double Kombinationen
    #S7 enhält alle Bullsye Triple Double
    #S8 enhält alle Single Double Kombinationen
    #S9 enhält alle Double Double Kombinationen
    #S10 enhält alle ein Dart Finishes (Double Kombinationen + 50)
    
    # Schritt 1: Erstellt die Punktzahlen für die möglichen Würfe
    U = np.concatenate((np.arange(1, 21), np.array([25])))  # Mögliche Single-Werte inklusive 25 (SBull)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))  # Mögliche Double-Werte
    T = 3 * np.arange(7, 21)  # Mögliche Triple-Werte (erst ab 7 sinnvoll)

    # Schritt 2: Erstellt alle Kombinationen [Double, Single, Triple]
    S = np.fliplr(combvec(D1, U, T))  # Reihenfolge: T, S, D (wegen fliplr)

    # Schritt 3: Berechnet die Summe der drei Würfe und hängt sie als vierte Spalte an
    T = S[:, 1] + S[:, 0] + S[:, 2]  # Summiert die ersten drei Spalten
    S = np.hstack((S, T[:, np.newaxis]))  # Hängt die Summe an

    # Schritt 4: Filtert nur Kombinationen, die exakt V ergeben
    Z = S[:, 3] == V  # Erstellt Maske für gültige Kombinationen
    S = np.hstack((S, Z[:, np.newaxis]))  # Hängt Maske als fünfte Spalte an
    S1 = S[S[:, 4] == 1, :]  # Bezieht nur gültige Kombinationen

    # Schritt 5: Erstellt eine Kopie für die Dart-Schreibweise
    S1_mapped = S1.astype(object)

    # Schritt 6: Wandelt Zahlen in Dart-Notation um
    for i in range(S1.shape[0]):
        for j in range(3):  # Geht jede der drei Spalten durch
            val = int(S1[i, j])  # Holt den numerischen Wert
            if j == 0:
                # Erster Wurf gilt als Triple
                S1_mapped[i, j] = f"T{val // 3}"
            elif j == 1:
                # Zweiter Wurf gilt als Single oder SBull
                if val == 25:
                    S1_mapped[i, j] = "SBull"
                else:
                    S1_mapped[i, j] = f"S{val}"
            else:
                # Dritter Wurf gilt als Double oder Bull
                if val == 50:
                    S1_mapped[i, j] = "Bull"
                else:
                    S1_mapped[i, j] = f"D{val // 2}"

    # Schritt 7: Hängt die Dart-Notation als weitere Spalten rechts an die numerischen Werte an
    S1 = np.hstack((S1, S1_mapped))
        
    # Erstellt die Werte für die Würfe:
    U = 2 * np.concatenate((np.arange(11, 21), np.array([25])))  # Nur gültige Double-Werte ab 11, inkl. 25
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))  # Alle möglichen Double-Werte
    T = U  # Für diese Kombination sind alle Würfe Doubles

    # Erstellt alle Kombinationen: [D, D, D]
    S = fliplr(combvec(D1, U, T))  # Geht jede mögliche Kombination durch
    T = S[:, 1] + S[:, 0] + S[:, 2]  # Berechnet die Summe
    S = np.hstack((S, T[:, np.newaxis]))  # Hängt die Summe als vierte Spalte an

    # Filtert alle Kombinationen, die exakt dem Wert V entsprechen
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))  # Hängt die Maske (True/False) an
    S2 = S[S[:, 4] == 1, :]  # Nimmt nur die Kombinationen mit passender Summe

    # Bereitet die Darstellung in Dart-Notation vor
    U = 2 * np.concatenate((np.arange(11, 21), np.array([25])))  # Wird für spätere Nutzung nochmals gesetzt
    S2_mapped = S2.astype(object)  # Kopie als Objekt-Array für String-Zuweisung

    # Wandelt alle drei Würfe in Dart-Schreibweise um
    for i in range(S2.shape[0]):
        for j in range(3):
            val = int(S2[i, j])  # Holt den numerischen Wert
            if j == 0:  # erster Wurf -> gilt als Double
                if val == 50:
                    S2_mapped[i, j] = "Bull"
                else:
                    S2_mapped[i, j] = f"D{val // 2}"
            elif j == 1:  # zweiter Wurf -> gilt ebenfalls als Double
                if val == 50:
                    S2_mapped[i, j] = "Bull"
                else:
                    S2_mapped[i, j] = f"D{val // 2}"
            else:  # letzter Wurf -> auch Double oder Bull
                if val == 50:
                    S2_mapped[i, j] = "Bull"
                else:
                    S2_mapped[i, j] = f"D{val // 2}"

    # Hängt die Dart-Schreibweise rechts an die numerischen Werte an
    S2 = np.hstack((S2, S2_mapped))

    # S2 spiegelt alle 2 2 2 Kombinationen wieder
    
    T= 2*np.concatenate((np.arange(11, 21), np.array([25])))
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    U = np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, T))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S3 = S[S[:, 4] == 1, :]
    S3_mapped = S3.astype(object)

    for i in range(S3.shape[0]):
        for j in range(3):
            val = int(S3[i, j])
            if j == 0:  # erster Wurf -> Triple
                if val == 50:
                    S3_mapped[i, j] = "Bull"
                else:
                    S3_mapped[i, j] = f"D{val // 2 }"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                if val == 25:
                    S3_mapped[i, j] = "SBull"
                else:
                    S3_mapped[i, j] = f"S{val }"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S3_mapped[i, j] = "Bull"
                else:
                    S3_mapped[i, j] = f"D{val // 2}"

    # Stacken: numerisch | Dart-Schreibweise
    S3 = np.hstack((S3, S3_mapped))
    #S3 spiegelt alle 2 1 2 Kombinationen wieder
     
    # Erstellung S4
    U = 3 * np.arange(7, 21)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    T = 3 * np.arange(7, 21)
    S = fliplr(combvec(D1, U, T))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S4 = S[S[:, 4] == 1, :]
    S4_mapped = S4.astype(object)
    for i in range(S4.shape[0]):
        for j in range(3):
            val = int(S4[i, j])
            if j == 0:  # erster Wurf -> Triple
                S4_mapped[i, j] = f"T{val // 3}"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                    S4_mapped[i, j] = f"T{val // 3}"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S4_mapped[i, j] = "Bull"
                else:
                    S4_mapped[i, j] = f"D{val // 2}"

# Stacken: numerisch | Dart-Schreibweise
    S4 = np.hstack((S4, S4_mapped))
    # S4 spiegelt alle 3 3 2  Kombinationen wieder

    #Erstellung von S5
    U = 2*np.concatenate((np.arange(11, 21), np.array([25])))
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    T = 3 * np.arange(7, 21)
    S = fliplr(combvec(D1, U, T))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S5 = S[S[:, 4] == 1, :]
    S5_mapped = S5.astype(object)
    for i in range(S5.shape[0]):
        for j in range(3):
            val = int(S5[i, j])
            if j == 0:  # erster Wurf -> Triple
                S5_mapped[i, j] = f"T{val // 3}"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                if val == 50:
                    S5_mapped[i, j] = "Bull"
                else:
                    S5_mapped[i, j] = f"D{val // 2}"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S5_mapped[i, j] = "Bull"
                else:
                    S5_mapped[i, j] = f"D{val // 2}"

    # Stacken: numerisch | Dart-Schreibweise
    S5 = np.hstack((S5, S5_mapped))
    #S5 spiegelt alle 3 2 2 Kombinationen wieder

    # Erstellung von S6
    U=np.concatenate((np.arange(1, 21), np.array([25])))
    B=50.*np.ones(1)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, B))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S6= S[S[:, 4] == 1, :]
    S6_mapped = S6.astype(object)
    for i in range(S6.shape[0]):
        for j in range(3):
            val = int(S6[i, j])
            if j == 0: 
                S6_mapped[i, j] = f"Bull"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                if val == 25:
                    S6_mapped[i, j] = "SBull"
                else:
                    S6_mapped[i, j] = f"S{val }"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S6_mapped[i, j] = "Bull"
                else:
                    S6_mapped[i, j] = f"D{val // 2}"

# Stacken: numerisch | Dart-Schreibweise
    S6 = np.hstack((S6, S6_mapped))
    # Erstellung 50 1 2 
    # Übergangsweise Lösung da man bei verschiedenen Kombinationen beim Verfehlen von Bull noch einen Outshot hat
    # langfristig Bull und 25 nicht als Single und Dopple behandeln sondern extra
    
        # Erstellung von S11
  # Hänge die Summe als neue Spalte an
    U = np.arange(1, 21)  
    B = 25. * np.ones(1)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, B))

    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]))

# Filtere die Zeilen, in denen die Summe == V ist
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))

# Nur die gültigen Kombinationen auswählen
    S31 = S[S[:, 4] == 1, :]
    S31_mapped = S31.astype(object)
    for i in range(S31.shape[0]):
        for j in range(3):
            val = int(S31[i, j])
            if j == 0: 
                S31_mapped[i, j] = f"SBull"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                if val == 25:
                    S31_mapped[i, j] = "SBull"
                else:
                    S31_mapped[i, j] = f"S{val }"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S31_mapped[i, j] = "Bull"
                else:
                    S31_mapped[i, j] = f"D{val // 2}"

    # Stacken: numerisch | Dart-Schreibweise
    S31 = np.hstack((S31, S31_mapped))

   
    
    
    
    # Erstellung S7
    U= 3 * np.arange(7, 21)
    B=50.*np.ones(1)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, B))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S7= S[S[:, 4] == 1, :]
    #  S7 steht für Bull 3 2
    S7_mapped = S7.astype(object)
    for i in range(S7.shape[0]):
        for j in range(3):
            val = int(S7[i, j])
            if j == 0: 
                S7_mapped[i, j] = f"Bull"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                S7_mapped[i, j] = f"T{val // 3}"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S7_mapped[i, j] = "Bull"
                else:
                    S7_mapped[i, j] = f"D{val // 2}"
    S7 = np.hstack((S7, S7_mapped))

    # Stacken: numerisch | Dart-Schreibweise
    #Erstellung S8
    U= 3 * np.arange(7, 21)
    B=0.*np.ones(1)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, B))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S8= S[S[:, 4] == 1, :]
    S8_mapped = S8.astype(object)
    for i in range(S8.shape[0]):
        for j in range(3):
            val = int(S8[i, j])
            if j == 0: 
                S8_mapped[i, j] = f"NA"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                S8_mapped[i, j] = f"T{val // 3}"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S8_mapped[i, j] = "Bull"
                else:
                    S8_mapped[i, j] = f"D{val // 2}"

    # Stacken: numerisch | Dart-Schreibweise
    S8 = np.hstack((S8, S8_mapped))
    # S8 spiegelt Tripple Double Combinationen wieder    

        ## 022
    U= 2*np.concatenate((np.arange(11, 21), np.array([25])))
    B=0.*np.ones(1)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, B))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S9= S[S[:, 4] == 1, :]
    S9_mapped = S9.astype(object)
    for i in range(S9.shape[0]):
        for j in range(3):
            val = int(S9[i, j])
            if j == 0: 
                S9_mapped[i, j] = f"NA"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                if val == 50:
                    S9_mapped[i, j] = "Bull"
                else:
                    S9_mapped[i, j] = f"D{val // 2}"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S9_mapped[i, j] = "Bull"
                else:
                    S9_mapped[i, j] = f"D{val // 2}"

    # Stacken: numerisch | Dart-Schreibweise
    S9 = np.hstack((S9, S9_mapped))
        ## 0 1 2
    U= np.concatenate((np.arange(1, 21), np.array([25])))
    B=0.*np.ones(1)
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, B))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S10= S[S[:, 4] == 1, :]
    S10_mapped = S10.astype(object)
    for i in range(S10.shape[0]):
        for j in range(3):
            val = int(S10[i, j])
            if j == 0: 
                S10_mapped[i, j] = f"NA"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                if val == 25:
                    S10_mapped[i, j] = "SBull"
                else:
                    S10_mapped[i, j] = f"S{val }"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S10_mapped[i, j] = "Bull"
                else:
                    S10_mapped[i, j] = f"D{val // 2}"

    # Stacken: numerisch | Dart-Schreibweise
    S10 = np.hstack((S10, S10_mapped))

        ## 002
    U= 0.*np.ones(1)
    B=U
    D1 = 2 * np.concatenate((np.arange(1, 21), np.array([25])))
    S = fliplr(combvec(D1, U, B))
    T = S[:, 1] + S[:, 0] + S[:, 2]
    S = np.hstack((S, T[:, np.newaxis]));
    Z = S[:, 3] == V
    S = np.hstack((S, Z[:, np.newaxis]))
    S11 = S[S[:, 4] == 1, :]
    S11_mapped = S11.astype(object)
    for i in range(S11.shape[0]):
        for j in range(3):
            val = int(S11[i, j])
            if j == 0: 
                S11_mapped[i, j] = f"NA"
            elif j == 1:  # zweiter Wurf -> Single oder SBull
                S11_mapped[i, j] = f"NA"
            else:  # letzter Wurf -> Double oder Bull
                if val == 50:
                    S11_mapped[i, j] = "Bull"
                else:
                    S11_mapped[i, j] = f"D{val // 2}"

    # Stacken: numerisch | Dart-Schreibweise
    S11 = np.hstack((S11, S11_mapped))
 ## definieren und zuordnen welche finishing wege wo gebraicht werden
    output_value=None
    if V < 41 and V % 2 == 0:  # kleiner als 41 und durch 2 teilbar -> 1-Dart-Finish
         output_value = S11
    elif V < 41 and V % 2 == 1:  # wenn nicht durch 2 Teilbar werden 2 darts benötigt
        output_value = S10[(S10[:, 2] % 4 == 0) & (S10[:, 1] != 25)]
    elif 41 <= V <= 49:
        output_value = S10[(S10[:, 1] != 25)]
    elif V == 50:
        output_value = np.vstack((S11, S10[:3])) # bei 50 beides möglich
    elif 51 <= V <= 60:
        output_value = S10
    elif 61 <= V <=80 and V % 2 == 0:
        output_value = np.vstack((S10, S9, S8, S6)) #
        output_value = output_value[(output_value[:, 1] != 50) & (output_value[:, 0]!= 50)  ] 
    elif 81 <= V < 86 and V % 2 == 0:
        output_value = np.vstack((S10, S9, S8)) #
        # hier reicht eine sigle Kombination nicht aus daher werden Tripple Dopple und Bull hinzugenommen
    elif 61 <= V < 80 and V % 2 == 1: #output_value = np.vstack((S10, S9, S8, S6,))
        output_value = np.vstack((S10, S9, S8, S6))
    elif 81 <= V < 86 and V % 2 == 1:
        output_value = np.vstack((S10, S9, S8, ))     
    elif 86 <= V < 90 and V % 2 == 0:
        output_value = np.vstack(( S8))
    elif 86 <= V <=90 and V % 2 == 1:
          output_value = np.vstack((S10, S9, S8, S6))
    elif 90 <= V <=97 and V % 2 == 1:
          output_value = np.vstack((S10, S9, S8, S6))  
    elif 90 <= V <=97 and V % 2 == 0:
          output_value = np.vstack((S10, S9, S8, S6,))            
    
    elif V == 98 or V==100:
        output_value = np.vstack((S8))
    elif V == 99 :
        output_value = np.vstack((S1))
    elif V == 101:
        output_value = np.vstack((S8,S1,S6))
    elif 100 < V < 105  or V==120:
            output_value = np.vstack((S10, S9, S8,S1))
    elif 104 < V <120 and V !=119:
            output_value = np.vstack((S10, S9, S8,S6,S1))

    
    elif   V ==99 :
            output_value = np.vstack((S10, S9, S8, S1))
    elif V==119:
            output_value = np.vstack((S10, S9, S8, S1, S2, S3, S1,S7,S5,S4))
    elif 120 < V  <=4000:
            output_value = np.vstack((S10, S9, S8, S1, S2, S3, S1,S7,S5,S4,S6)) ### wird im 2ten Schritt besser gefiltert
    
    output_value = output_value[:, :10] ## 
    output_value = output_value
    V_minus_50_times_3 = (V - 50) * 3 
    exclude_50 = (
    (V - 20 < 101 and V - 20 != 99) or
    (V - 19 < 101 and V - 19 != 99) or
    (V - 18 < 101 and V - 18 != 99) or
    (V - 17 < 101 and V - 17 != 99)
    
    
)
    
    
        
    if (61 <= V <= 75):
        selected_rows = output_value[
        (output_value[:, 0] == 0) &  
        (output_value[:, 1] > 48) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == V_minus_50_times_3) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 40) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 32) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 16) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == 25) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 24) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 36)|
        (output_value[:, 0] == 0) &
        (output_value[:, 2] ==output_value[:, 1])]

    elif (76 <= V <= 80):
        selected_rows = output_value[
        (output_value[:, 0] == 0) &  
        (output_value[:, 1] > 48) &  (output_value[:, 1] != 50) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == V_minus_50_times_3) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 40) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 32) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 16) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == 25) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 24) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 36)|
        (output_value[:, 0] == 0) &
        (output_value[:, 2] ==output_value[:, 1]) 
        
    ] 
    elif (90 <= V <= 95) :
        selected_rows = output_value[
       (output_value[:, 0] == 0) |
       ((output_value[:, 0] == 50) &  # Added parentheses for clarity
        (output_value[:, 2]  == 40) |(output_value[:, 2]  == 32)|(output_value[:, 2]  == 16) ) 
    ] 
    elif (96 <= V <= 97) :
        selected_rows = output_value[
       (output_value[:, 0] == 0) 
    ] 
    elif (V == 99):
        selected_rows = output_value[((((V - output_value[:, 0] / 3) == 80) & ((output_value[:, 2] == 32)| (output_value[:, 2] == 40))))]
    elif (V == 98 or V==100) :
        selected_rows = output_value[
       (output_value[:, 0] == 0) ] 
    elif (81 <= V <= 85):
        selected_rows = output_value[
        (output_value[:, 0] == 0) &  
        (output_value[:, 1] > 48) &  (output_value[:, 1] != 50) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == V_minus_50_times_3) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 40) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 32) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 16) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == 25) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 24) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 36) |
        (output_value[:, 1] == 50) |
        ((output_value[:, 0] == 25) & ((output_value[:, 2] == 40) | (output_value[:, 2] == 24)))|
        ((output_value[:, 0] == 50) & ((output_value[:, 2] == 24) | (output_value[:, 2] == 16)))

        
    ] 
    elif (2 <= V <= 40):
        selected_rows = output_value
        
    elif (86 <= V <= 90) and V % 2 == 0 or (V == 100):
        selected_rows = output_value[(output_value[:, 0] == 0) &  
        (output_value[:, 1] >= 48) &  (output_value[:, 1] != 50) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == V_minus_50_times_3) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 40) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 32) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 16) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == 25) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 24) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 36) |
        (output_value[:, 1] == 50) |
        (output_value[:, 0] == output_value[:, 2]) &
        (output_value[:, 2] % 4 == 0) |
        (output_value[:, 0] == 32) &
        (output_value[:, 2] == 40)|
        (output_value[:, 0] == 36) &
        (output_value[:, 2] == 40)|
        (output_value[:, 0] == 32) & 
        (output_value[:, 2] == 40)|
        (output_value[:, 1] == (output_value[:, 2] / 2)) &
        (output_value[:, 0] % 4 == 0)]
        
    elif (86 <= V <= 90) and V % 2 == 1:
        selected_rows = output_value[(output_value[:, 0] == 0) &  # Überprüfung auf Null in der ersten Spalte
        (output_value[:, 1] >= 48) &  (output_value[:, 1] != 50) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == V_minus_50_times_3) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 40) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 32) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 16) |
        (output_value[:, 0] == 0) &
        (output_value[:, 1] == 25) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 24) |
        (output_value[:, 0] == 0) &
        (output_value[:, 2] == 36) |
        (output_value[:, 0] == output_value[:, 2]) &
        (output_value[:, 2] % 4 == 0)&
        (output_value[:, 1] != 25) |
        (output_value[:, 0] == 32) &
        (output_value[:, 2] == 40)&
        (output_value[:, 1] != 25)|
        (output_value[:, 0] == 36) &
        (output_value[:, 2] == 40)&  
        (output_value[:, 1] != 25)|
        (output_value[:, 0] == 32) &
        (output_value[:, 2] == 40)&  (output_value[:, 1] != 25)|
        (output_value[:, 1] == (output_value[:, 2] / 2)) &
        (output_value[:, 0] % 4 == 0) &
        (output_value[:, 1] != 25) ]
    elif V == 101 or V == 102 or V == 103 or V == 104 :
        selected_rows = output_value[
        ((output_value[:, 0] == 0) | 
        ((output_value[:, 0] == 50) & ((output_value[:, 2] == 32) | (output_value[:, 2] == 40))) | 
        (((output_value[:, 0] != 50) & (output_value[:, 2] == 32)) | ((output_value[:, 0] != 50) & (output_value[:, 2] == 40))) | 
        ((output_value[:, 2] == output_value[:, 0]) & (output_value[:, 2] != 50))) &
        (output_value[:, 1] != 25) # This ensures the second column is not 25
    ]
    elif (105 <= V <= 118) or V == 120:
        selected_rows = output_value[
        # Bedingung: erste Zahl ist nicht 50
        (output_value[:, 0] != 50) &
        # Berechnung von (V - erste Zahl / 3), und das Ergebnis ist nicht in der Liste [109, 108, 106, 103, 102, 99]
        ~np.isin(V - (output_value[:, 0] / 3), [109, 108, 106, 103, 102, 99]) &
        # Bedingung: zweite Zahl ist nicht 25 und dritte Zahl ist nicht 50
        (output_value[:, 1] != 25) &
        # Bedingung: dritte Zahl ist entweder 32 oder 40 oder die zweite Zahl ist die Hälfte der dritten Zahl
        ((output_value[:, 2] == 32) | (output_value[:, 2] == 40) | (output_value[:, 2] / 2 == output_value[:, 1])) |
        # Wenn die erste Zahl 50 ist, prüfen, ob V - 25 in der Liste [80, 108, 106, 103, 102, 99]
        (((output_value[:, 0] == 50) & np.isin(V - 25, [80])) & (((output_value[:, 2] == 32) | (output_value[:, 2] == 40) | (output_value[:, 2] / 2 == output_value[:, 1]))))|(output_value[:, 0] == 0)
    ] 

    elif  119 <= V <= 123:
        selected_rows = output_value[
    ((output_value[:, 0] != 50) &  # Erste Spalte ist nicht 50
     (output_value[:, 2] != 50) &  # Dritte Spalte ist nicht 50
     (output_value[:, 1] != 25) &  # Zweite Spalte ist nicht 25
     ~np.isin(V - (output_value[:, 0] / 3), [109, 108, 106, 103, 102, 99]) &  # Wert darf nicht in der Liste sein
      (V- output_value[:, 0] - (output_value[:, 1] / 3) == 50))  # Spezifische Bedingung
    |
    ((output_value[:, 0] == 50) &  # Erste Spalte ist 50
     (V - 25 < 99 or V - 25 == 100) &  # Erste Bedingung muss erfüllt sein
     (not exclude_50) &  # Falls eine der Bedingungen `True` ist, wird 50 ausgeschlossen
         (V - 50 - (output_value[:, 1] / 3) <= 59)&(output_value[:, 1] != 50) )  # Falls eine der Bedingungen `True` ist, wird 50 ausgeschlossen
    ] # Specific condition
        
  # Check various values of V
    elif  124 <= V <= 130:
        selected_rows = output_value[(output_value[:, 0] != 50) &  # Erste Spalte ist nicht 50
     (output_value[:, 2] != 50) & np.isin(V - (output_value[:, 0] / 3), [110, 107, 104, 101, 100, 98]) & (output_value[:, 1] != 50) & (V- output_value[:, 0] - (output_value[:, 1] / 3) <= 60)  |(output_value[:, 0] == 50) &  
     ((V - 25 < 99 or V - 25 == 100)& (V- output_value[:, 0] - (output_value[:, 1] / 3) <= 60))
    ]
    
    elif V == 132 or V==131 or V==133:
        selected_rows = output_value[
        (output_value[:, 0] != 50)&(output_value[:, 1] != 50) & 
        ((V - output_value[:, 0] - (output_value[:, 1] / 3)) <= 60) |((output_value[:, 0] == 50) &(output_value[:, 1] == 50)) |(output_value[:, 2] == output_value[:, 1]) & 
             (output_value[:, 2] != 50) & 
             (output_value[:, 1] != 50)
    ]
    elif V == 135 or  V == 134:
        selected_rows = output_value[
        (output_value[:, 0] != 50) &
        (output_value[:, 1] != 50) & 
            ((V - output_value[:, 0] - (output_value[:, 1] / 3)) <= 60) | 
            ((output_value[:, 2] == output_value[:, 1]) & 
             (output_value[:, 2] != 50) & 
             (output_value[:, 1] != 50)) | (output_value[:, 0] == 50) &  (V- 25 == 110)
    ]
    elif V == 136 or V==137 or V==138 or V==13999:
        selected_rows = output_value[
        (output_value[:, 0] != 50) &
        (output_value[:, 1] != 50) &
        (
            (
                (output_value[:, 1] > 40) &
                (output_value[:, 1] % 3 == 0) &
                ((V - output_value[:, 0] - (output_value[:, 1] / 3)) <= 60)
            ) |
            (
                (output_value[:, 1] < 40) &
                (output_value[:, 1] % 2 == 0) &
                ((V - output_value[:, 0] - (output_value[:, 1] / 2)) <= 60)
            )
        )
    ]
    elif V == 139:
        selected_rows = output_value[
        (output_value[:, 0] != 50) &
        (output_value[:, 1] != 50) &
        (output_value[:, 1] > 40) &
        (output_value[:, 1] % 3 == 0) &
        (
            ((V - output_value[:, 0] - (output_value[:, 1] / 3)) <= 60) |
            (
                ((V - output_value[:, 0] - (output_value[:, 1] / 3)) <= 70) &
                (np.isin(output_value[:, 2], [32, 40]))
            )
        ) | (output_value[:, 1] == 50) & (np.isin(output_value[:, 2], [32, 40,16]))
    ]
    elif V == 140:
        selected_rows = output_value[
        (output_value[:, 0] != 50) &
        (output_value[:, 1] != 50) &
        (output_value[:, 1] > 40) &
        (output_value[:, 1] % 3 == 0) &
        ((V - output_value[:, 0] - (output_value[:, 1] / 3)) <= 70) &
        (
            (output_value[:, 1] == output_value[:, 0]) |
            (
                (output_value[:, 1] > 47) &
                (output_value[:, 0] > 47)
            ) |
            (
                (output_value[:, 1] == output_value[:, 2]) & (output_value[:, 2] != 50)
            )
        )
    ]
    elif V in [141, 142, 143, 144,145,146,147,149,150 ]:
        selected_rows = output_value[
        (
            (output_value[:, 1] == 50) & 
            (((V - output_value[:, 0] - 25) <= 60) | ((V - output_value[:, 0] - 25) == 65))
        ) 
        | 
        (
            (output_value[:, 0] != 50) & 
            (output_value[:, 1] != 50) & 
            ((V - output_value[:, 0] - (output_value[:, 1] / 3)) <= 70)
        )
    ]
    elif V in [151]:
        selected_rows = output_value[(output_value[:, 0] != 50) & 
            (output_value[:, 1] != 50) &(output_value[:, 2] != 50)  ]
    elif V in [152]:
        selected_rows = output_value[(output_value[:, 0] != 50) & 
            (output_value[:, 1] != 50) &(output_value[:, 2] != 50) | (output_value[:, 1] == output_value[:, 2]) ]
    elif  153 <= V <= 170:
        selected_rows = output_value
    
    else:
        selected_rows = []
    return  selected_rows[:, 5:8]


    
def print_solution(V):
    if V == 159 or V == 162 or V == 163 or V == 165 or V == 166 or V == 168 or V == 169 or V > 170 or V == 1:    
        return "No possible outshot"
    else:
        return "Good Luck"
@app.route('/', methods=['GET', 'POST'])
def index():
    output_value = None
    print_solution_message = None

    if request.method == 'POST':
        V = float(request.form['input_value'])
        output_value = calculate_output(V)
        print_solution_message = print_solution(V)
        
        


    return render_template('index.html', output_value=output_value, print_solution_message=print_solution_message)

if __name__ == '__main__':
    app.run(debug=True)











