# Script pour pousser le projet sur GitHub
cd "C:\Users\Merieme SOSSEY\Desktop\hackthon"

# Initialiser git si ce n'est pas déjà fait
if (-not (Test-Path .git)) {
    git init
    Write-Host "Git initialisé"
} else {
    Write-Host "Git déjà initialisé"
}

# Ajouter le remote (remplace l'ancien s'il existe)
git remote remove origin 2>$null
git remote add origin git@github.com:Yassirsossey11/hackathon-project-.git
Write-Host "Remote ajouté"

# Ajouter tous les fichiers
git add .
Write-Host "Fichiers ajoutés"

# Faire un commit
git commit -m "Initial commit: Reputation Analysis Platform with AI features"
Write-Host "Commit créé"

# Pousser vers GitHub
Write-Host "Poussage vers GitHub..."
git branch -M main
git push -u origin main

Write-Host "Terminé! Vérifiez votre repository GitHub."

