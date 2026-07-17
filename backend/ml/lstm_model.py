import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, precision_recall_curve

from preprocess import load_and_clean, FEATURES

def build_sequences(df, window: int = 20):

    sequences, labels = [], []
    for eq_class, group in df.groupby("equipment_class"):
        group = group.sort_values("operating_minutes").reset_index(drop=True)
        values= group[FEATURES].values
        fail = group["failure"].values
        for i in range(len(group) - window):
            sequences.append(values[i:i + window])
            labels.append(int(fail[i + window - 1]))
    return np.array(sequences), np.array(labels)

class SequenceDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.X) 

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    
class FailureLSTM(nn.Module):
    def __init__(self, n_features=5, hidden_size=64, num_layers=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout,
        )    
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )
    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        return self.classifier(h_n[-1]).squeeze(-1)

def train(csv_path: str ="data/ai4i2020.csv", epochs: int=30, window: int =20,
          batch_size: int =64, lr: float =1e-3, patience : int = 5) :
        df = load_and_clean(csv_path)
        X, y = build_sequences(df, window=window)
        print(f"Séquence construites : {len(X)}, taux de panne ; {y.mean():.2%}")

        mean, std = X.mean(axis=(0,1)), X.std(axis=(0, 1)) + 1e-6
        X = (X -mean) / std   

        from sklearn.model_selection import train_test_split as sk_split

        X_train, X_val, y_train , y_val = sk_split(X, y, test_size=0.2, stratify=y, random_state=42)
        train_ds = SequenceDataset(X_train, y_train)
        val_ds = SequenceDataset(X_val, y_val)
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device utilisé : {device}")
        model = FailureLSTM(n_features=X.shape[2]).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)

        pos_weight = torch.tensor([0.5* (1 - y.mean()) / (y.mean() + 1e-6)]).to (device)
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

        best_val_loss = float("inf")
        epochs_no_improve = 0
        best_state = None

        for epoch in range(epochs):
            model.train()
            total_loss = 0
            for xb, yb in train_loader :
                xb, yb = xb.to(device), yb.to(device)
                optimizer.zero_grad()
                loss = criterion(model(xb), yb)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * len(xb)
            train_loss = total_loss / len(train_ds)

            model.eval()
            val_loss, all_preds, all_probs, all_labels =0 , [], [], []
            with torch.no_grad():
                for xb, yb in  val_loader:
                    xb, yb = xb.to(device), yb.to(device)
                    logits = model(xb)
                    val_loss += criterion(logits, yb).item() * len(xb)
                    probs = torch.sigmoid(logits)
                    all_probs.extend(probs.cpu().numpy())
                    all_preds.extend((probs > 0.5).float().cpu().numpy())
                    all_labels.extend(yb.cpu().numpy())
            val_loss /= len(val_ds)
            scheduler.step(val_loss)

            print(f"Epoch {epoch+1}/{epochs} - train_loss : {train_loss:.4f} - val_loss: {val_loss:.4f}")

            if val_loss< best_val_loss:
                best_val_loss = val_loss
                best_state = model.state_dict()
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"Early stopping à l'epoch {epoch +1} (pas d'amélioration depuis {patience} epochs)")
                    break
        model.load_state_dict(best_state)

        print("\n ===  Évaluation finale (meilleur modèle) === ")
        print(classification_report(all_labels, all_preds, digits=3, target_names=["Normal", "Panne"]))
        print(f"ROC-AUC / {roc_auc_score(all_labels, all_probs):.3f}")      
        print (f"Matrice de cconfusion :\n {confusion_matrix(all_labels, all_preds)}")

        precisions, recalls, thresholds = precision_recall_curve(all_labels, all_probs)
        beta = 2
        f2_scores =(1 + beta**2) * (precisions * recalls) / (beta**2 * precisions + recalls + 1e-10)
        best_idx = f2_scores.argmax()
        print(f"\nMeillerur seuil (F2 optimal) : {thresholds[best_idx]:.3f}")
        print(f"À ce seuil -> precision: {precisions[best_idx]:.3}, recall: {recalls[best_idx]:.3f}")    
        
        torch.save({
            "model_state": model.state_dict(),
            "mean": mean, "std": std, "window": window,
            "n_features": X.shape[2],

        }, "data/lstm_model.pt")         
        print("\nModèle sauvergadré : data/lstm_model.pt")
        return model

if __name__ == "__main__":
    train()    


                   