import { useState, useEffect } from "react";

export default function Editoras() {
  const [editoras, setEditoras] = useState([]);
  const [novaEditora, setNovaEditora] = useState("");
  const [mostrarForm, setMostrarForm] = useState(false);

  const token = localStorage.getItem("token"); // pega o token armazenado

  // Função para carregar todas as editoras
  const carregarEditoras = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/editoras/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Erro ao carregar editoras");

      const data = await response.json();
      setEditoras(data);
    } catch (error) {
      console.error("Falha ao carregar editoras:", error);
    }
  };

  useEffect(() => {
    carregarEditoras();
  }, []);

  // Função para criar uma nova editora
  const handleCriarEditora = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/api/editoras/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ nome: novaEditora }),
      });

      if (!response.ok) {
        const erroData = await response.json();
        throw new Error(erroData.detail || "Erro ao criar editora");
      }

      const nova = await response.json();
      setEditoras([...editoras, nova]);
      setNovaEditora("");
      setMostrarForm(false);
    } catch (error) {
      console.error("Falha ao criar editora:", error);
      alert(`Falha ao criar editora: ${error.message}`);
    }
  };

  return (
    <div className="editoras-container">
      <h2>Editoras</h2>

      <button
        className="btn-criar"
        onClick={() => setMostrarForm(!mostrarForm)}
      >
        Criar Editora
      </button>

      {mostrarForm && (
        <form className="form-editora" onSubmit={handleCriarEditora}>
          <input
            type="text"
            placeholder="Nome da editora"
            value={novaEditora}
            onChange={(e) => setNovaEditora(e.target.value)}
          />

          <button type="submit" className="btn-salvar">
            Salvar
          </button>
        </form>
      )}

      <table className="editoras-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome da Editora</th>
          </tr>
        </thead>

        <tbody>
          {editoras.map((e) => (
            <tr key={e.id_grupo || e.id_editora || e.id}>
              <td>{e.id_editora}</td>
              <td>{e.nome}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
