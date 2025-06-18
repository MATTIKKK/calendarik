import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
} from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import { User } from '../types/user';
import { RegisterData } from '../types/auth';

/* ---------- тип контекста ---------- */
export type AuthContextType = {
  user: User | null;
  setUser: (user: User | null) => void;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/* ---------- базовый URL лучше тянуть из env ---------- */
const API_URL = import.meta.env.VITE_API_URL || 'http://128.251.224.196:8000/api';

/* ====================================================================== */
/*                              PROVIDER                                   */
/* ====================================================================== */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('accessToken')
  );
  const [loading, setLoading] = useState(true);

  /* единственный таймер, «привязанный» к экземпляру провайдера */
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* ---------- вспомогалки ---------- */

  /** Ставит/сбрасывает таймер авто-обновления */
  const scheduleRefresh = (delayMs: number) => {
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    if (delayMs <= 0) return; // если токен уже протух — не ждём
    refreshTimer.current = setTimeout(refreshAccessToken, delayMs);
  };

  /** Сохраняем токены + планируем обновление */
  const setTokens = (accessToken: string, refreshToken: string) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    setToken(accessToken);

    // смотрим срок жизни access-токена
    const { exp } = jwtDecode<{ exp: number }>(accessToken);
    // обновимся за минуту до конца
    const delayMs = exp * 1000 - Date.now() - 60_000;
    scheduleRefresh(delayMs);
  };

  /* ---------- API-запросы ---------- */

  /** Получить новый access по refresh */
  const refreshAccessToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) return logout();

      const { data } = await axios.post(`/api/auth/refresh`, {
        refresh_token: refreshToken,
      });

      setTokens(data.access_token, data.refresh_token);
    } catch (err) {
      console.error('Refresh token failed → logout', err);
      logout(); // не уходим в рекурсию
    }
  };

  /** Подтянуть профиль текущего пользователя */
  const fetchUser = async () => {
    try {
      const accessToken = localStorage.getItem('accessToken');
      if (!accessToken) return;

      const { data } = await axios.get(`/api/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      setUser(data);
      // если мы здесь — токен валиден, убедимся что таймер стоит
      const { exp } = jwtDecode<{ exp: number }>(accessToken);
      scheduleRefresh(exp * 1000 - Date.now() - 60_000);
    } catch (err) {
      console.error('Fetch user failed', err);
      // Если access протух → сразу пытаемся обновить
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        await refreshAccessToken();
      }
    }
  };

  /* ---------- действия для UI ---------- */

  const login = async (email: string, password: string) => {
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);

    const { data } = await axios.post(`/api/auth/login`, body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    setTokens(data.access_token, data.refresh_token);
    await fetchUser();
  };

  const register = async (form: RegisterData) => {
    setLoading(true);
    try {
      await axios.post(`/api/auth/register`, form);
      await login(form.email, form.password);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    setUser(null);
    setToken(null);
    window.location.href = '/';
  };

  /* ---------- инициализация ---------- */
  useEffect(() => {
    fetchUser().finally(() => setLoading(false));

    // подчистка таймера при размонтировании
    return () => {
      if (refreshTimer.current) clearTimeout(refreshTimer.current);
    };
  }, []);

  /* ---------- значение контекста ---------- */
  const value: AuthContextType = {
    user,
    setUser,   
    token,
    loading,
    login,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/* ====================================================================== */
/*                               HOOK                                     */
/* ====================================================================== */
export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
