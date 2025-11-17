import { useState, useEffect } from "react";

export default function Emprestimos() {
    const [emprestimos, setEmprestimos] = useState([]);
    const [clientes, setClientes] = useState([]);
    const [livros, setLivros] = useState([]);
    const [clienteSelecionado, setClienteSelecionado] = useState("");
    const [livroSelecionado, setLivroSelecionado] = useState("");
    const [mostrarForm, setMostrarForm] = useState(false);

    const token = localStorage.getItem("token");

    // Carregar clientes
    useEffect(() => {
        async function carregarClientes() {
            try {
                const res = await fetch("http://127.0.0.1:8000/api/clientes/", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (!res.ok) throw new Error("Erro ao carregar clientes");
                const data = await res.json();
                setClientes(data);
            } catch (error) {
                console.error("Erro:", error);
                alert("Erro ao carregar clientes: " + error.message);
            }
        }
        carregarClientes();
    }, [token]);

    // Carregar livros
    useEffect(() => {
        async function carregarLivros() {
            try {
                const res = await fetch("http://127.0.0.1:8000/api/livros/", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (!res.ok) throw new Error("Erro ao buscar livros");
                const data = await res.json();
                setLivros(data);
            } catch (error) {
                console.error("Erro:", error);
                alert("Erro ao carregar livros: " + error.message);
            }
        }
        carregarLivros();
    }, [token]);

    // Criar empréstimo
    const handleCriarEmprestimo = async (e) => {
        e.preventDefault();

        if (!clienteSelecionado || !livroSelecionado) {
            alert("Selecione cliente e livro");
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
                    id_cliente: clienteSelecionado,   // <--- ajustar aqui
                    id_exemplar: livroSelecionado,    // <--- e aqui
                }),
            });

            const data = await res.json();

            if (!res.ok) {
                alert(data.detail || "Erro ao criar empréstimo");
                return;
            }

            setEmprestimos([...emprestimos, data]);
            setClienteSelecionado("");
            setLivroSelecionado("");
            setMostrarForm(false);
        } catch (error) {
            alert("Erro inesperado: " + error.message);
        }
    };


    // Finalizar empréstimo
    const finalizarEmprestimo = async (id) => {
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/emprestimos/${id}/finalizar`, {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
            });

            const data = await res.json();

            if (!res.ok) {
                alert(data.detail || "Erro ao finalizar empréstimo");
                return;
            }

            setEmprestimos(
                emprestimos.map((emp) =>
                    emp.id_emprestimo === id ? { ...emp, status: "Finalizado" } : emp
                )
            );

            alert(data.message || "Empréstimo finalizado com sucesso");
        } catch (error) {
            alert("Erro inesperado: " + error.message);
        }
    };

    return (
        <div className="emprestimos-container">
            <h2>Empréstimos</h2>

            <button className="btn-criar" onClick={() => setMostrarForm(!mostrarForm)}>
                Criar Empréstimo
            </button>

            {mostrarForm && (
                <form className="form-emprestimo" onSubmit={handleCriarEmprestimo}>
                    <label>Cliente:</label>
                    <select
                        value={clienteSelecionado}
                        onChange={(e) => setClienteSelecionado(e.target.value)}
                    >
                        <option value="">Selecione o cliente</option>
                        {clientes.map((c) => (
                            <option key={c.id_cliente} value={c.id_cliente}>
                                {c.nome} {c.sobrenome || ""}
                            </option>
                        ))}
                    </select>

                    <label>Livro:</label>
                    <select
                        value={livroSelecionado}
                        onChange={(e) => setLivroSelecionado(e.target.value)}
                    >
                        <option value="">Selecione o livro</option>
                        {livros.map((l) => (
                            <option key={l.id_livro} value={l.id_livro}>
                                {l.titulo}
                            </option>
                        ))}
                    </select>

                    <button type="submit" className="btn-salvar">
                        Salvar
                    </button>
                </form>
            )}

            <table className="emprestimos-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Cliente</th>
                        <th>Livro</th>
                        <th>Data</th>
                        <th>Status</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody>
                    {emprestimos.map((emp) => (
                        <tr key={emp.id_emprestimo}>
                            <td>{emp.id_emprestimo}</td>
                            <td>{emp.cliente?.nome || emp.cliente}</td>
                            <td>{emp.exemplar?.livro?.titulo || emp.exemplar}</td>
                            <td>{emp.data_emprestimo?.split("T")[0]}</td>
                            <td>{emp.status ? "Ativo" : "Finalizado"}</td>
                            <td>
                                {emp.status ? (
                                    <button
                                        className="btn-finalizar"
                                        onClick={() => finalizarEmprestimo(emp.id_emprestimo)}
                                    >
                                        Finalizar
                                    </button>
                                ) : (
                                    <span className="finalizado">Finalizado</span>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
