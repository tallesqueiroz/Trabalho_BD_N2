import React, { useEffect, useState } from "react";

export default function Clientes() {
  const [clientes, setClientes] = useState([]);
  const [novoCliente, setNovoCliente] = useState({
    nome: "",
    email: "",
    cpf: "",
    telefone: "",
  });
  const [mostrarForm, setMostrarForm] = useState(false);

  const token = localStorage.getItem("token");

  // Carregar clientes
  useEffect(() => {
    async function carregarClientes() {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/clientes/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error("Erro ao carregar clientes");

        const data = await response.json();
        setClientes(data);
      } catch (error) {
        console.error("Erro:", error);
      }
    }

    carregarClientes();
  }, [token]);

  // Criar cliente
  const handleCriarCliente = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/api/clientes/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(novoCliente),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Falha ao criar cliente");
      }

      const clienteCriado = await response.json();
      setClientes([...clientes, clienteCriado]);
      setNovoCliente({ nome: "", email: "", cpf: "", telefone: "" });
      setMostrarForm(false);
    } catch (error) {
      alert(`Falha ao criar cliente: ${error.message}`);
    }
  };

  return (
    <div className="clientes-container">
      <h2>Clientes</h2>

      <button onClick={() => setMostrarForm(!mostrarForm)}>
        Criar Cliente
      </button>

      {mostrarForm && (
        <form onSubmit={handleCriarCliente} className="form-cliente">
          <input
            type="text"
            placeholder="Nome"
            value={novoCliente.nome}
            onChange={(e) =>
              setNovoCliente({ ...novoCliente, nome: e.target.value })
            }
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={novoCliente.email}
            onChange={(e) =>
              setNovoCliente({ ...novoCliente, email: e.target.value })
            }
            required
          />
          <input
            type="text"
            placeholder="CPF"
            value={novoCliente.cpf}
            onChange={(e) =>
              setNovoCliente({ ...novoCliente, cpf: e.target.value })
            }
            required
          />
          <input
            type="text"
            placeholder="Telefone (opcional)"
            value={novoCliente.telefone}
            onChange={(e) =>
              setNovoCliente({ ...novoCliente, telefone: e.target.value })
            }
          />
          <button type="submit">Salvar</button>
        </form>
      )}

      <table className="clientes-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Email</th>
            <th>CPF</th>
            <th>Telefone</th>
          </tr>
        </thead>
        <tbody>
          {clientes.map((c) => (
            <tr key={c.id_cliente}>
              <td>{c.id_cliente}</td>
              <td>{c.nome}</td>
              <td>{c.email}</td>
              <td>{c.cpf}</td>
              <td>{c.telefone || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
