import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Livros() {
  const [livros, setLivros] = useState([]);
  const [editoras, setEditoras] = useState([]);
  const [autores, setAutores] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [mostrarForm, setMostrarForm] = useState(false);

  const [novoLivro, setNovoLivro] = useState({
    titulo: "",
    isbn: "",
    ano_publicacao: "",
    id_editora: "",
    autores: [],      // array de IDs
    categorias: [],   // array de IDs
  });

  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  // Buscar livros
  useEffect(() => {
    async function fetchLivros() {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/livros/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Erro ao buscar livros");
        const data = await res.json();
        setLivros(data);
      } catch (error) {
        console.error(error);
      }
    }
    fetchLivros();
  }, [token]);

  // Buscar editoras, autores e categorias para os selects
  useEffect(() => {
    const fetchEditoras = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/editoras/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Erro ao carregar editoras");
        setEditoras(await res.json());
      } catch (error) {
        console.error(error);
      }
    };

    const fetchAutores = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/autores/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Erro ao carregar autores");
        setAutores(await res.json());
      } catch (error) {
        console.error(error);
      }
    };

    const fetchCategorias = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/categorias/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Erro ao carregar categorias");
        setCategorias(await res.json());
      } catch (error) {
        console.error(error);
      }
    };

    fetchEditoras();
    fetchAutores();
    fetchCategorias();
  }, [token]);

  // Criar livro
  const handleCriarLivro = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:8000/api/livros/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...novoLivro,
          ano_publicacao: novoLivro.ano_publicacao || null,
          autores_ids: novoLivro.autores,
          categorias_ids: novoLivro.categorias,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        // Exibe o erro do backend em um alerta
        alert(err.detail || "Erro ao criar livro");
        return; // para não continuar
      }

      const criado = await res.json();
      setLivros([...livros, criado]);

      // Reset do formulário
      setNovoLivro({
        titulo: "",
        isbn: "",
        ano_publicacao: "",
        id_editora: "",
        autores: [],
        categorias: [],
      });
      setMostrarForm(false);
    } catch (error) {
      // Exibe qualquer outro erro em alerta
      alert("Falha ao criar livro: " + error.message);
      console.error("Falha ao criar livro:", error.message);
    }
  };


  return (
    <div className="livros-container">
      <h2>Livros</h2>
      <button className="btn-criar" onClick={() => setMostrarForm(!mostrarForm)}>
        Criar Livro
      </button>

      {mostrarForm && (
        <form className="form-livro" onSubmit={handleCriarLivro}>
          <input
            type="text"
            placeholder="Título"
            value={novoLivro.titulo}
            onChange={(e) => setNovoLivro({ ...novoLivro, titulo: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="ISBN"
            value={novoLivro.isbn}
            onChange={(e) => setNovoLivro({ ...novoLivro, isbn: e.target.value })}
          />
          <input
            type="number"
            placeholder="Ano de publicação"
            value={novoLivro.ano_publicacao}
            onChange={(e) =>
              setNovoLivro({ ...novoLivro, ano_publicacao: e.target.value })
            }
          />

          <select
            value={novoLivro.id_editora}
            onChange={(e) => setNovoLivro({ ...novoLivro, id_editora: e.target.value })}
            required
          >
            <option value="">Selecione a editora</option>
            {editoras.map((ed) => (
              <option key={ed.id_editora} value={ed.id_editora}>
                {ed.nome}
              </option>
            ))}
          </select>

          <label>Autores:</label>
          <select
            multiple
            value={novoLivro.autores}
            onChange={(e) =>
              setNovoLivro({
                ...novoLivro,
                autores: Array.from(e.target.selectedOptions, (opt) => opt.value),
              })
            }
          >
            {autores.map((a) => (
              <option key={a.id_autor} value={a.id_autor}>
                {a.nome} {a.sobrenome}
              </option>
            ))}
          </select>

          <label>Categorias:</label>
          <select
            multiple
            value={novoLivro.categorias}
            onChange={(e) =>
              setNovoLivro({
                ...novoLivro,
                categorias: Array.from(e.target.selectedOptions, (opt) => opt.value),
              })
            }
          >
            {categorias.map((c) => (
              <option key={c.id_categoria} value={c.id_categoria}>
                {c.nome}
              </option>
            ))}
          </select>

          <button type="submit" className="btn-salvar">
            Salvar
          </button>
        </form>
      )}

      <table className="livros-table">
        <thead>
          <tr>
            <th>ID Livro</th>
            <th>Título</th>
            <th>ISBN</th>
            <th>Ano</th>
            <th>Editora</th>
            <th>Autores</th>
            <th>Categorias</th>
            <th>Exemplares</th>
          </tr>
        </thead>
        <tbody>
          {livros.map((l) => (
            <tr key={l.id_livro}>
              <td>{l.id_livro}</td>
              <td>{l.titulo}</td>
              <td>{l.isbn || "-"}</td>
              <td>{l.ano_publicacao || "-"}</td>
              <td>{l.editora?.nome || "-"}</td>
              <td>
                {l.autores.length > 0
                  ? l.autores.map((a) => `${a.nome} ${a.sobrenome || ""}`).join(", ")
                  : "-"}
              </td>
              <td>
                {l.categorias.length > 0
                  ? l.categorias.map((c) => c.nome).join(", ")
                  : "-"}
              </td>
              <td>
                <button
                  className="btn-exemplares"
                  onClick={() => navigate(`/exemplares/${l.id_livro}`)}
                >
                  Ver Exemplares
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
