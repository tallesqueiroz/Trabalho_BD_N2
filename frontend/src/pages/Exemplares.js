import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export default function Exemplares() {
  const { idLivro } = useParams();
  const [exemplares, setExemplares] = useState([]);
  const [mostrarFormExemplar, setMostrarFormExemplar] = useState(false);
  const [codigo, setCodigo] = useState("");
  const [status, setStatus] = useState("Disponível");
  const [localizacao, setLocalizacao] = useState("");

  const [clientes, setClientes] = useState([]);
  const [mostrarFormEmprestimo, setMostrarFormEmprestimo] = useState(false);
  const [clienteSelecionado, setClienteSelecionado] = useState(null);
  const [exemplarParaEmprestimo, setExemplarParaEmprestimo] = useState(null);

  const token = localStorage.getItem("token");

  // Carregar exemplares
  useEffect(() => {
    async function fetchExemplares() {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/exemplares/por-livro/${idLivro}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Erro ao buscar exemplares");
        }
        setExemplares(await res.json());
      } catch (error) {
        console.error(error.message);
      }
    }
    fetchExemplares();
  }, [idLivro, token]);

  // Carregar clientes
  useEffect(() => {
    async function fetchClientes() {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/clientes/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Erro ao carregar clientes");
        setClientes(await res.json());
      } catch (error) {
        console.error(error.message);
      }
    }
    fetchClientes();
  }, [token]);

  // Criar exemplar
  const handleCriarExemplar = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:8000/api/exemplares/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          id_livro: idLivro,
          codigo_barras: codigo,
          status,
          localizacao,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erro ao criar exemplar");
      }
      const novoExemplar = await res.json();
      setExemplares([...exemplares, novoExemplar]);
      setCodigo("");
      setStatus("Disponível");
      setLocalizacao("");
      setMostrarFormExemplar(false);
    } catch (error) {
      alert("Erro ao criar exemplar: " + error.message);
    }
  };

  // Criar empréstimo
  const handleCriarEmprestimo = async (e) => {
    e.preventDefault();
    if (!clienteSelecionado || !exemplarParaEmprestimo) {
      alert("Selecione um cliente.");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/api/emprestimos/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          id_cliente: parseInt(clienteSelecionado),
          id_exemplar: parseInt(exemplarParaEmprestimo),
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erro ao criar empréstimo");
      }

      alert("Empréstimo criado com sucesso!");
      setMostrarFormEmprestimo(false);
      setClienteSelecionado(null);
      setExemplarParaEmprestimo(null);
    } catch (error) {
      alert("Falha ao criar empréstimo: " + error.message);
    }
  };

  return (
    <div className="exemplares-container">
      <h2>Exemplares do Livro {idLivro}</h2>

      <button onClick={() => setMostrarFormExemplar(!mostrarFormExemplar)}>
        Criar Exemplar
      </button>

      {mostrarFormExemplar && (
        <form onSubmit={handleCriarExemplar} className="form-exemplar">
          <input
            type="text"
            placeholder="Código do exemplar"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Localização"
            value={localizacao}
            onChange={(e) => setLocalizacao(e.target.value)}
          />
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option>Disponível</option>
            <option>Emprestado</option>
          </select>
          <button type="submit">Salvar</button>
        </form>
      )}

      {mostrarFormEmprestimo && (
        <form onSubmit={handleCriarEmprestimo} className="form-emprestimo">
          <select
            value={clienteSelecionado || ""}
            onChange={(e) => setClienteSelecionado(e.target.value)}
            required
          >
            <option value="">Selecione o cliente</option>
            {clientes.map((c) => (
              <option key={c.id_cliente} value={c.id_cliente}>
                {c.nome} {c.sobrenome || ""}
              </option>
            ))}
          </select>

          <button type="submit">Confirmar Empréstimo</button>
        </form>
      )}

      <table className="exemplares-table">
        <thead>
          <tr>
            <th>ID Exemplar</th>
            <th>Código</th>
            <th>Status</th>
            <th>Localização</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          {exemplares.length > 0 ? (
            exemplares.map((ex) => (
              <tr key={ex.id_exemplar}>
                <td>{ex.id_exemplar}</td>
                <td>{ex.codigo_barras || "-"}</td>
                <td>{ex.status}</td>
                <td>{ex.localizacao || "-"}</td>
                <td>
                  {ex.status === "Disponível" && (
                    <button
                      onClick={() => {
                        setExemplarParaEmprestimo(ex.id_exemplar);
                        setMostrarFormEmprestimo(true);
                      }}
                    >
                      Fazer Empréstimo
                    </button>
                  )}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={5}>Nenhum exemplar encontrado.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
