# Apenas um script rápido para gerar um hash
# Rode isso uma vez no seu terminal

from security import get_password_hash

# Escolha uma senha forte para seu primeiro admin
senha_admin = "admin@biblioteca2025" 

hash_da_senha = get_password_hash(senha_admin[:72])


print("\n--- HASH DA SENHA PARA O ADMIN ---")
print(hash_da_senha)
print("--------------------------------------\n")