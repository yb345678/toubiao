import { Navigate, Outlet } from "react-router-dom";
import { isAuthenticated } from "../store/authStore";

export function ProtectedRoute() {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
