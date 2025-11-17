import { Link } from "react-router-dom";

export default function Dashboard() {
  return (
    <div className="dashboard-container">
      <h1>BiblioTech – Dashboard</h1>

      <div className="dashboard-grid">
        <Link to="/clientes" className="dashboard-card">Clientes</Link>
        <Link to="/livros" className="dashboard-card">Livros</Link>
        <Link to="/autores" className="dashboard-card">Autores</Link>
        <Link to="/categorias" className="dashboard-card">Categorias</Link>
        <Link to="/editoras" className="dashboard-card">Editoras</Link>
        <Link to="/emprestimos" className="dashboard-card">Empréstimos</Link>
        <Link to="/me" className="dashboard-card">Meu Perfil</Link>
      </div>
    </div>
  );
}
