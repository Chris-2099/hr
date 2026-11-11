import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../AuthContext";

interface EmployeeRow {
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  department_id: string;
  employment_status: string;
  employee_type: string;
  hire_date: string;
  remote_type: string;
  last_performance_rating: string | null;
  base_salary?: number | null;
  compa_ratio?: number | null;
}

export default function Employees() {
  const { user } = useAuth();
  const [rows, setRows] = useState<EmployeeRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<EmployeeRow[]>("/api/employees?limit=300")
      .then(setRows)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Employee Directory</h2>
        <p>
          {user?.department_scope
            ? `Scoped to your assigned departments: ${user.department_scope.join(", ")}`
            : "All departments (your role has unrestricted access)."}
        </p>
      </div>
      <div className="card">
        {rows.length === 0 ? (
          <div className="loading">Loading…</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Department</th>
                <th>Status</th>
                <th>Type</th>
                <th>Hire Date</th>
                <th>Work Arrangement</th>
                <th>Last Rating</th>
                {user?.can_view_compensation && <th>Base Salary</th>}
                {user?.can_view_compensation && <th>Compa-Ratio</th>}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.employee_id}>
                  <td>
                    {r.first_name} {r.last_name}
                  </td>
                  <td>{r.department_id}</td>
                  <td>
                    <span className="badge">{r.employment_status}</span>
                  </td>
                  <td>{r.employee_type}</td>
                  <td>{r.hire_date}</td>
                  <td>{r.remote_type}</td>
                  <td>{r.last_performance_rating ?? "—"}</td>
                  {user?.can_view_compensation && <td>{r.base_salary ? `$${Math.round(r.base_salary).toLocaleString()}` : "—"}</td>}
                  {user?.can_view_compensation && <td>{r.compa_ratio ?? "—"}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
