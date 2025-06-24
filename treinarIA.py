import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Carrega os dados
df = pd.read_csv("dados_csv/letras.csv")

# Separa características (X) e rótulos (y)
X = df.drop("letra", axis=1)
y = df["letra"]

# Divide em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Cria e treina o modelo
modelo = KNeighborsClassifier(n_neighbors=3)
modelo.fit(X_train, y_train)

# Avaliação
y_pred = modelo.predict(X_test)
print("📊 Acurácia:", accuracy_score(y_test, y_pred))
print("\n📋 Relatório de Classificação:\n", classification_report(y_test, y_pred))

# Salva o modelo treinado
joblib.dump(modelo, "modelo_letras_knn.pkl")
print("✅ Modelo salvo como 'modelo_letras_knn.pkl'")