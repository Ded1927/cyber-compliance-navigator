import DownloadIcon from "@mui/icons-material/Download";
import FlagIcon from "@mui/icons-material/Flag";
import LoginIcon from "@mui/icons-material/Login";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useState } from "react";

import { apiClient } from "../../api/client";

type AnonymousTask = {
  index: number;
  title: string;
  description: string;
  guidance: string | null;
  references: string | null;
  legal_basis: string;
  deadline_days: number;
};

type AnonymousRoadmapViewProps = {
  tasks: AnonymousTask[];
  orgTypeLabel: string;
  onGoToLogin: () => void;
};

export function AnonymousRoadmapView({
  tasks,
  orgTypeLabel,
  onGoToLogin,
}: AnonymousRoadmapViewProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<AnonymousTask | null>(null);

  const handleExportPdf = async () => {
    setIsExporting(true);
    setExportError(null);

    try {
      const response = await apiClient.post(
        "/questionnaire/anonymous-export-pdf",
        { org_type_label: orgTypeLabel, tasks },
        { responseType: "blob" },
      );

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "roadmap.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch {
      setExportError("Не вдалося експортувати PDF. Спробуйте ще раз.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h2" component="h2">
          Ваша дорожня карта
        </Typography>
        <Typography color="text.secondary">
          {tasks.length} кроків для «{orgTypeLabel}». Це попередній перегляд —
          зареєструйтесь, щоб відстежувати прогрес.
        </Typography>
      </Box>

      {exportError && <Alert severity="error">{exportError}</Alert>}

      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          disabled={isExporting}
          onClick={handleExportPdf}
        >
          {isExporting ? "Експорт..." : "Експортувати в PDF"}
        </Button>
        <Button variant="outlined" startIcon={<LoginIcon />} onClick={onGoToLogin}>
          Увійти для повного доступу
        </Button>
      </Box>

      <Stack spacing={2}>
        {tasks.map((task) => (
          <Box
            key={task.index}
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "44px 1fr" },
              gap: 2,
              alignItems: "stretch",
            }}
          >
            <Box
              sx={{
                display: { xs: "none", md: "flex" },
                alignItems: "center",
                flexDirection: "column",
              }}
            >
              <Box
                sx={{
                  width: 34,
                  height: 34,
                  borderRadius: "50%",
                  bgcolor: "primary.main",
                  color: "primary.contrastText",
                  display: "grid",
                  placeItems: "center",
                  fontWeight: 700,
                }}
              >
                {task.index}
              </Box>
              <Box sx={{ width: 2, flexGrow: 1, bgcolor: "divider", mt: 1 }} />
            </Box>

            <Card
              variant="outlined"
              sx={{ borderRadius: 2, cursor: "pointer", "&:hover": { borderColor: "primary.light" } }}
              onClick={() => setSelectedTask(task)}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      flexDirection: { xs: "column", sm: "row" },
                      gap: 1.5,
                    }}
                  >
                    <Box>
                      <Typography variant="h3" component="h3">
                        {task.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        {task.legal_basis} · строк виконання: {task.deadline_days} днів
                      </Typography>
                    </Box>
                    <Chip
                      icon={<FlagIcon />}
                      label="Попередній перегляд"
                      color="info"
                      variant="outlined"
                      sx={{ alignSelf: { xs: "flex-start", sm: "center" } }}
                    />
                  </Box>
                  <Typography color="text.secondary">{task.description}</Typography>
                </Stack>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Stack>

      <Box
        sx={{
          p: 3,
          borderRadius: 2,
          bgcolor: "rgba(18, 53, 91, 0.04)",
          border: "1px dashed",
          borderColor: "primary.light",
          textAlign: "center",
        }}
      >
        <Typography variant="h3" component="p">
          Потрібен повний функціонал?
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 1, mb: 2 }}>
          Зареєструйтесь, щоб відстежувати прогрес виконання кроків, отримувати
          підказки та генерувати документи.
        </Typography>
        <Button variant="contained" startIcon={<LoginIcon />} onClick={onGoToLogin}>
          Перейти до входу
        </Button>
      </Box>

      {/* Task detail dialog */}
      <Dialog
        open={Boolean(selectedTask)}
        onClose={() => setSelectedTask(null)}
        fullWidth
        maxWidth="md"
      >
        {selectedTask && (
          <>
            <DialogTitle sx={{ pr: 7 }}>
              {selectedTask.title}
              <IconButton
                aria-label="Закрити"
                onClick={() => setSelectedTask(null)}
                sx={{ position: "absolute", right: 12, top: 12 }}
              >
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent dividers>
              <Stack spacing={2.5}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Правова основа
                  </Typography>
                  <Typography>{selectedTask.legal_basis}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Строк виконання
                  </Typography>
                  <Typography>{selectedTask.deadline_days} днів</Typography>
                </Box>
                <Box>
                  <Typography variant="h3" component="h3">
                    Опис
                  </Typography>
                  <Typography sx={{ mt: 1 }} color="text.secondary">
                    {selectedTask.description}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="h3" component="h3">
                    Підказки
                  </Typography>
                  <Typography sx={{ mt: 1 }} color="text.secondary">
                    {selectedTask.guidance || "Підказки для цього кроку ще не додані."}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="h3" component="h3">
                    Референси
                  </Typography>
                  <Typography sx={{ mt: 1 }} color="text.secondary">
                    {selectedTask.references || "Референси для цього кроку ще не додані."}
                  </Typography>
                </Box>
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                disabled={isExporting}
                onClick={handleExportPdf}
              >
                Експортувати PDF
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Stack>
  );
}
