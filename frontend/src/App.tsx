import type { ReactNode } from "react";
import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import LoginIcon from "@mui/icons-material/Login";
import RouteIcon from "@mui/icons-material/Route";
import SecurityIcon from "@mui/icons-material/Security";
import FactCheckIcon from "@mui/icons-material/FactCheck";
import StorageIcon from "@mui/icons-material/Storage";

import { apiClient } from "./api/client";
import { Layout } from "./components/Layout";
import { QuestionnaireFeature } from "./features/questionnaire";
import { RoadmapView } from "./features/roadmap";
import { AnonymousRoadmapView } from "./features/roadmap/AnonymousRoadmapView";

type CurrentUser = {
  id: number;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
};

type AnonymousTask = {
  index: number;
  title: string;
  description: string;
  guidance: string | null;
  references: string | null;
  legal_basis: string;
  deadline_days: number;
};

type AppMode = "landing" | "login" | "anonymous-questionnaire" | "anonymous-roadmap";

const orgTypeLabels: Record<string, string> = {
  state_body: "Орган державної влади",
  local_gov: "Орган місцевого самоврядування",
  state_enterprise: "Державне підприємство",
  private: "Приватна компанія",
};

export function App() {
  const queryClient = useQueryClient();
  const [isQuestionnaireDone, setIsQuestionnaireDone] = useState(false);
  const [appMode, setAppMode] = useState<AppMode>("landing");

  // Anonymous roadmap state
  const [anonymousTasks, setAnonymousTasks] = useState<AnonymousTask[]>([]);
  const [anonymousOrgTypeLabel, setAnonymousOrgTypeLabel] = useState("");

  const { data: currentUser, isLoading: isAuthLoading } = useQuery<CurrentUser | null>({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      try {
        const response = await apiClient.get<CurrentUser>("/auth/me");
        return response.data;
      } catch {
        return null;
      }
    },
    retry: false,
    refetchOnWindowFocus: false,
  });

  const handleLogout = async () => {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Even if the server session is already gone, return the UI to login state.
    }
    queryClient.setQueryData(["auth", "me"], null);
    setIsQuestionnaireDone(false);
    setAppMode("landing");
  };

  const handleAnonymousComplete = (tasks: AnonymousTask[], orgType: string) => {
    setAnonymousTasks(tasks);
    setAnonymousOrgTypeLabel(orgTypeLabels[orgType] || orgType);
    setAppMode("anonymous-roadmap");
  };

  if (isAuthLoading) {
    return (
      <Box sx={{ display: "grid", minHeight: "100vh", placeItems: "center" }}>
        <CircularProgress />
      </Box>
    );
  }

  // --- Authenticated flow ---
  if (currentUser) {
    if (!isQuestionnaireDone) {
      return (
        <Layout user={currentUser} onLogout={handleLogout}>
          <QuestionnaireFeature onComplete={() => setIsQuestionnaireDone(true)} />
        </Layout>
      );
    }

    return (
      <Layout user={currentUser} onLogout={handleLogout}>
        <DashboardContent user={currentUser}>
          <RoadmapView />
          <SystemRegisterWidget canEdit={currentUser.is_admin} />
        </DashboardContent>
      </Layout>
    );
  }

  // --- Anonymous flow ---
  if (appMode === "login") {
    return <LoginScreen onBack={() => setAppMode("landing")} />;
  }

  if (appMode === "anonymous-questionnaire") {
    return (
      <AnonymousShell>
        <QuestionnaireFeature
          anonymous
          onAnonymousComplete={handleAnonymousComplete}
          onGoToLogin={() => setAppMode("login")}
        />
      </AnonymousShell>
    );
  }

  if (appMode === "anonymous-roadmap") {
    return (
      <AnonymousShell>
        <AnonymousRoadmapView
          tasks={anonymousTasks}
          orgTypeLabel={anonymousOrgTypeLabel}
          onGoToLogin={() => setAppMode("login")}
        />
      </AnonymousShell>
    );
  }

  // --- Landing page ---
  return <LandingPage onAnonymous={() => setAppMode("anonymous-questionnaire")} onLogin={() => setAppMode("login")} />;
}

// ---------------------------------------------------------------------------
// Landing page
// ---------------------------------------------------------------------------

type LandingPageProps = {
  onAnonymous: () => void;
  onLogin: () => void;
};

function LandingPage({ onAnonymous, onLogin }: LandingPageProps) {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.default",
      }}
    >
      {/* Hero */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #0A223A 0%, #12355B 40%, #2F5C86 100%)",
          color: "white",
          py: { xs: 8, md: 12 },
          px: 3,
          textAlign: "center",
        }}
      >
        <Box sx={{ maxWidth: 720, mx: "auto" }}>
          <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
            <SecurityIcon sx={{ fontSize: 56, opacity: 0.9 }} />
          </Box>
          <Typography variant="h1" sx={{ fontSize: { xs: "1.75rem", md: "2.5rem" }, mb: 2 }}>
            CyberLaw Navigator
          </Typography>
          <Typography sx={{ fontSize: { xs: "1rem", md: "1.2rem" }, opacity: 0.85, mb: 5, lineHeight: 1.7 }}>
            Визначте ваші зобов&apos;язання у сфері кібербезпеки за кілька хвилин.
            Отримайте персоналізовану дорожню карту з конкретними кроками та
            правовими підставами.
          </Typography>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="center">
            <Button
              variant="contained"
              size="large"
              startIcon={<RouteIcon />}
              onClick={onAnonymous}
              sx={{
                bgcolor: "white",
                color: "primary.dark",
                fontWeight: 700,
                px: 4,
                py: 1.5,
                "&:hover": { bgcolor: "rgba(255,255,255,0.9)" },
              }}
            >
              Сформувати дорожню карту
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<LoginIcon />}
              onClick={onLogin}
              sx={{
                borderColor: "rgba(255,255,255,0.5)",
                color: "white",
                px: 4,
                py: 1.5,
                "&:hover": { borderColor: "white", bgcolor: "rgba(255,255,255,0.1)" },
              }}
            >
              Увійти в кабінет
            </Button>
          </Stack>
        </Box>
      </Box>

      {/* Features */}
      <Box sx={{ maxWidth: 960, mx: "auto", px: 3, py: { xs: 6, md: 8 }, width: "100%" }}>
        <Typography variant="h2" textAlign="center" sx={{ mb: 5 }}>
          Що ви отримуєте?
        </Typography>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
            gap: 3,
          }}
        >
          <FeatureCard
            icon={<FactCheckIcon sx={{ fontSize: 40, color: "primary.main" }} />}
            title="Опитувальник"
            text="Визначаємо тип організації, роботу з ДІР/ІзОД та належність до ОКІ/ОКІІ для точного підбору вимог."
          />
          <FeatureCard
            icon={<RouteIcon sx={{ fontSize: 40, color: "primary.main" }} />}
            title="Дорожня карта"
            text="Отримуєте персоналізований перелік кроків із правовою основою, строками та підказками для виконання."
          />
          <FeatureCard
            icon={<StorageIcon sx={{ fontSize: 40, color: "primary.main" }} />}
            title="Повний кабінет"
            text="Зареєстровані користувачі відстежують прогрес, генерують документи та ведуть реєстр систем."
          />
        </Box>
      </Box>

      {/* Anonymous vs Registered comparison */}
      <Box sx={{ bgcolor: "rgba(18,53,91,0.03)", py: { xs: 5, md: 7 }, px: 3 }}>
        <Box sx={{ maxWidth: 720, mx: "auto", textAlign: "center" }}>
          <Typography variant="h2" sx={{ mb: 2 }}>
            Без реєстрації vs Повний доступ
          </Typography>
          <Box
            component="table"
            sx={{
              width: "100%",
              borderCollapse: "collapse",
              mt: 3,
              "& th, & td": { py: 1.5, px: 2, textAlign: "left", borderBottom: "1px solid", borderColor: "divider" },
              "& th": { fontWeight: 700, color: "text.primary" },
              "& td": { color: "text.secondary" },
            }}
          >
            <thead>
              <tr>
                <th>Функція</th>
                <th>Без реєстрації</th>
                <th>Зареєстрований</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Опитувальник</td><td>✅</td><td>✅</td></tr>
              <tr><td>Генерація дорожньої карти</td><td>✅</td><td>✅</td></tr>
              <tr><td>Експорт у PDF</td><td>✅</td><td>✅</td></tr>
              <tr><td>Збереження прогресу</td><td>❌</td><td>✅</td></tr>
              <tr><td>Редагування кроків</td><td>❌</td><td>✅</td></tr>
              <tr><td>Генерація документів</td><td>❌</td><td>✅</td></tr>
              <tr><td>Реєстр систем</td><td>❌</td><td>✅</td></tr>
            </tbody>
          </Box>

          <Button
            variant="contained"
            size="large"
            startIcon={<RouteIcon />}
            onClick={onAnonymous}
            sx={{ mt: 4, px: 4, py: 1.5 }}
          >
            Спробувати безкоштовно
          </Button>
        </Box>
      </Box>

      {/* Footer */}
      <Box sx={{ py: 3, px: 3, textAlign: "center", borderTop: "1px solid", borderColor: "divider" }}>
        <Typography variant="body2" color="text.secondary">
          © 2026 CyberLaw Navigator · Кабінет кіберкомплаєнсу
        </Typography>
      </Box>
    </Box>
  );
}

type FeatureCardProps = {
  icon: ReactNode;
  title: string;
  text: string;
};

function FeatureCard({ icon, title, text }: FeatureCardProps) {
  return (
    <Paper variant="outlined" sx={{ p: 3, borderRadius: 2, textAlign: "center", height: "100%" }}>
      <Box sx={{ mb: 2 }}>{icon}</Box>
      <Typography variant="h3" sx={{ mb: 1 }}>
        {title}
      </Typography>
      <Typography color="text.secondary">{text}</Typography>
    </Paper>
  );
}

// ---------------------------------------------------------------------------
// Anonymous shell (simplified layout without sidebar for non-logged-in users)
// ---------------------------------------------------------------------------

function AnonymousShell({ children }: { children: ReactNode }) {
  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <Box
        sx={{
          bgcolor: "white",
          borderBottom: "1px solid",
          borderColor: "divider",
          px: 3,
          py: 2,
          display: "flex",
          alignItems: "center",
          gap: 1.5,
        }}
      >
        <SecurityIcon color="primary" />
        <Typography variant="h3" component="div" sx={{ color: "primary.main" }}>
          CyberLaw Navigator
        </Typography>
      </Box>
      <Box sx={{ maxWidth: 960, mx: "auto", px: { xs: 2, sm: 3 }, py: 4 }}>{children}</Box>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Login screen
// ---------------------------------------------------------------------------

function LoginScreen({ onBack }: { onBack?: () => void }) {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLogin = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await apiClient.post<CurrentUser>("/auth/login", {
        email,
        password,
      });
      queryClient.setQueryData(["auth", "me"], response.data);
    } catch (loginError) {
      if (axios.isAxiosError(loginError)) {
        setError(loginError.response?.data?.detail ?? "Не вдалося увійти.");
      } else {
        setError("Не вдалося увійти.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        bgcolor: "background.default",
        px: 2,
      }}
    >
      <Paper variant="outlined" sx={{ width: "100%", maxWidth: 460, p: 3, borderRadius: 2 }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h2" component="h1">
              Вхід до CyberLaw Navigator
            </Typography>
            <Typography sx={{ mt: 1 }} color="text.secondary">
              Тестові ролі: користувач може формувати дорожню карту, адміністратор може редагувати
              кроки, підказки та референси.
            </Typography>
          </Box>

          {error && <Alert severity="error">{error}</Alert>}

          <TextField
            label="Email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            fullWidth
          />
          <TextField
            label="Пароль"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            fullWidth
          />

          <Button variant="contained" disabled={isSubmitting} onClick={handleLogin}>
            {isSubmitting ? "Вхід..." : "Увійти"}
          </Button>

          {onBack && (
            <Button variant="text" onClick={onBack}>
              ← Повернутися на головну
            </Button>
          )}

          <Paper variant="outlined" sx={{ p: 2, borderRadius: 1, bgcolor: "action.hover" }}>
            <Typography variant="body2" color="text.secondary">
              Користувач: user@cyberlaw.ua / User12345!
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Адміністратор: admin@cyberlaw.ua / Admin12345!
            </Typography>
          </Paper>
        </Stack>
      </Paper>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Dashboard (authenticated)
// ---------------------------------------------------------------------------

type DashboardContentProps = {
  children: ReactNode;
  user: CurrentUser;
};

function DashboardContent({ children, user }: DashboardContentProps) {
  return (
    <Stack spacing={3}>
      <Box id="dashboard">
        <Typography variant="h2" component="h1">
          Кабінет кіберкомплаєнсу
        </Typography>
        <Typography color="text.secondary">
          {user.is_admin
            ? "Адміністратор може редагувати каталог кроків, підказки та референси."
            : "Користувач формує дорожню карту та виконує призначені кроки."}
        </Typography>
      </Box>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
          gap: 2,
        }}
      >
        <StatusCard label="Ваша дорожня карта" value="Активна" />
        <StatusCard label="Статус готовності" value="У роботі" />
        <StatusCard
          label="Роль"
          value={user.is_admin ? "Адміністратор" : "Користувач"}
        />
      </Box>

      {children}
    </Stack>
  );
}

type StatusCardProps = {
  label: string;
  value: string;
};

function StatusCard({ label, value }: StatusCardProps) {
  return (
    <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, height: "100%" }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h3" component="p" sx={{ mt: 1 }}>
        {value}
      </Typography>
    </Paper>
  );
}

type SystemRegisterWidgetProps = {
  canEdit: boolean;
};

function SystemRegisterWidget({ canEdit }: SystemRegisterWidgetProps) {
  return (
    <Paper id="systems" variant="outlined" sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h3" component="h2">
        Реєстр систем
      </Typography>
      <Typography sx={{ mt: 1 }} color="text.secondary">
        {canEdit
          ? "Адміністратор може налаштовувати довідники та вимоги для систем."
          : "Користувач переглядає та наповнює інформацію про свої системи."}
      </Typography>
    </Paper>
  );
}
