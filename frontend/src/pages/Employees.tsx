import { useEffect, useState } from "react";
import { api } from "../api";
import DataTable from "../components/table/DataTable";
import { useAuth } from "../AuthContext";

type Employee = {
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  department_id: string;
  employment_status: string;
  employee_type: string;
  hire_date: string;
  base_salary: number | null;
  compa_ratio: number | null;
};

export default function Employees() {
  const { user } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setEmployees(await api.get<Employee[]>("/employees"));
      } catch {
        setError("Couldn't load employees.");
      }
    })();
  }, []);

  if (error) return <p className="text-sm text-red-600">{error}</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold text-slate-900">Employees</h1>
      <DataTable
        rows={employees}
        rowKey={(e) => e.employee_id}
        columns={[
          { header: "Name", render: (e) => `${e.first_name} ${e.last_name}` },
          { header: "Email", render: (e) => e.email },
          { header: "Department", render: (e) => e.department_id },
          { header: "Status", render: (e) => e.employment_status },
          { header: "Type", render: (e) => e.employee_type },
          { header: "Hired", render: (e) => e.hire_date },
          ...(user?.can_view_compensation
            ? [
                {
                  header: "Base Salary",
                  render: (e: Employee) =>
                    e.base_salary != null ? `$${e.base_salary.toLocaleString()}` : "—",
                },
              ]
            : []),
        ]}
      />
    </div>
  );
}
