import React, { useEffect, useState } from "react";

export default function Categorias() {
  const [categorias, setCategorias] = useState([]);
  const [novaCategoria, setNovaCategoria] = useState("");
  const [mostrarForm, setMostrarForm] = useState(false);

  useEffect(() => {
    async function carregarCategorias() {
      try {
        const token = localStorage.getItem("token");

        const response = await fetch("http://127.0.0.1:8000/api/categorias/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) throw new Error("Erro ao carregar categorias");

        const data = await response.json();
        setCategorias(data);
      } catch (error) {
        console.error("Erro:", error);
      }
    }

    carregarCategorias();
  }, []);

  const handleCriarCategoria = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem("token");

      const response = await fetch("http://127.0.0.1:8000/api/categorias/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          nome: novaCategoria,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Falha ao criar categoria");
      }

      const categoriaCriada = await response.json();
      setCategorias([...categorias, categoriaCriada]);
      setNovaCategoria("");
      setMostrarForm(false);
    } catch (error) {
      alert(`Falha ao criar categoria: ${error.message}`);
    }
  };

  return (
    <div className="categorias-container">
      <h2>Categorias</h2>

      <button
        className="btn-criar"
        onClick={() => setMostrarForm(!mostrarForm)}
      >
        Criar Categoria
      </button>

      {mostrarForm && (
        <form className="form-categoria" onSubmit={handleCriarCategoria}>
          <input
            type="text"
            placeholder="Nome da categoria"
            value={novaCategoria}
            onChange={(e) => setNovaCategoria(e.target.value)}
            required
          />
          <button type="submit" className="btn-salvar">
            Salvar
          </button>
        </form>
      )}

      <table className="categorias-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome da Categoria</th>
          </tr>
        </thead>

        <tbody>
          {categorias.map((c) => (
            <tr key={c.id_categoria}>
              <td>{c.id_categoria}</td>
              <td>{c.nome}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
