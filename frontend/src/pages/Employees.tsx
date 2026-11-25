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

type Department = { department_id: string; name: string };

function StatusBadge({ status }: { status: string }) {
  const isActive = status === "Active";
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        isActive ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"
      }`}
    >
      {status}
    </span>
  );
}

export default function Employees() {
  const { user } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [emps, depts] = await Promise.all([
          api.get<Employee[]>("/employees"),
          api.get<Department[]>("/departments"),
        ]);
        setEmployees(emps);
        setDepartments(depts);
      } catch {
        setError("Couldn't load employees.");
      }
    })();
  }, []);

  if (error) return <p className="text-sm text-red-600">{error}</p>;

  const deptName = new Map(departments.map((d) => [d.department_id, d.name]));

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Employees</h1>
        <p className="mt-1 text-sm text-slate-500">{employees.length} people across the organization.</p>
      </div>
      <DataTable
        rows={employees}
        rowKey={(e) => e.employee_id}
        columns={[
          { header: "Name", render: (e) => `${e.first_name} ${e.last_name}` },
          { header: "Email", render: (e) => e.email },
          { header: "Department", render: (e) => deptName.get(e.department_id) ?? e.department_id },
          { header: "Status", render: (e) => <StatusBadge status={e.employment_status} /> },
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
