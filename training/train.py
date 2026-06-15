import os
import glob
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
from PIL import Image
from collections import Counter

DATA_ROOT = r"data/Train_Validation sets/Train_Validation sets"
CLASSES = ["Normal", "Suspect", "Keratoconus"]
MAP_SUFFIX = "_Sag_A.jpg"
BATCH_SIZE = 16
EPOCHS = 25
LEARNING_RATE = 0.0001
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class TopographyDataset(Dataset):
    def __init__(self, root, classes, suffix):
        self.samples = []
        for idx, cls in enumerate(classes):
            cls_path = os.path.join(root, cls)
            for case_folder in os.listdir(cls_path):
                case_path = os.path.join(cls_path, case_folder)
                matches = glob.glob(os.path.join(case_path, f"*{suffix}"))
                if matches:
                    self.samples.append((matches[0], idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        return image, label


class TransformWrapper(Dataset):
    """Wraps a dataset subset and applies a given transform."""
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):
        image, label = self.subset[idx]
        return self.transform(image), label


train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(5),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def main():
    print(f"Using device: {DEVICE}")

    raw_dataset = TopographyDataset(DATA_ROOT, CLASSES, MAP_SUFFIX)
    print(f"Total samples found: {len(raw_dataset)}")

    label_counts = Counter(label for _, label in raw_dataset.samples)
    print(f"Class distribution: { {CLASSES[k]: v for k, v in label_counts.items()} }")

    val_size = int(0.2 * len(raw_dataset))
    train_size = len(raw_dataset) - val_size
    train_subset, val_subset = random_split(raw_dataset, [train_size, val_size])

    train_dataset = TransformWrapper(train_subset, train_transform)
    val_dataset = TransformWrapper(val_subset, val_transform)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Class weights to handle imbalance (Normal=150, Suspect=123, Keratoconus=99)
    total = sum(label_counts.values())
    class_weights = torch.tensor(
        [total / label_counts[i] for i in range(len(CLASSES))],
        dtype=torch.float32
    ).to(DEVICE)

    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    model = model.to(DEVICE)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3)

    best_val_acc = 0.0

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)

        train_loss = running_loss / len(train_dataset)

        model.eval()
        correct = 0
        total_val = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                total_val += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_acc = correct / total_val
        scheduler.step(val_acc)
        current_lr = optimizer.param_groups[0]['lr']
        print(f"Epoch {epoch+1}/{EPOCHS} - Train Loss: {train_loss:.4f} - Val Acc: {val_acc:.4f} - LR: {current_lr:.6f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "best_model.pth")

    with open("class_mapping.json", "w") as f:
        json.dump({"classes": CLASSES, "map_suffix": MAP_SUFFIX}, f)

    print(f"Training complete. Best validation accuracy: {best_val_acc:.4f}")


if __name__ == "__main__":
    main()