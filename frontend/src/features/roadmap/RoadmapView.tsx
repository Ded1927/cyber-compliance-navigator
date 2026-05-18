import CloseIcon from "@mui/icons-material/Close";
import EditIcon from "@mui/icons-material/Edit";
import FlagIcon from "@mui/icons-material/Flag";
import SaveIcon from "@mui/icons-material/Save";
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import { apiClient } from "../../api/client";

type RoadmapTask = {
  id: string;
  organization_id: string;
  title: string;
  description: string;
  guidance: string | null;
  references: string | null;
  status: "PENDING" | "IN_PROGRESS" | "DONE" | string;
  legal_basis: string;
  deadline_days: number;
};

type RoadmapTaskDraft = {
  title: string;
  description: string;
  guidance: string;
  references: string;
  legal_basis: string;
  deadline_days: string;
};

const statusLabels: Record<string, string> = {
  PENDING: "Очікує виконання",
  IN_PROGRESS: "У роботі",
  DONE: "Виконано",
};

export function RoadmapView() {
  const [tasks, setTasks] = useState<RoadmapTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<RoadmapTask | null>(null);
  const [draft, setDraft] = useState<RoadmapTaskDraft | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [canEditRoadmap, setCanEditRoadmap] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const completedCount = useMemo(
    () => tasks.filter((task) => task.status === "DONE").length,
    [tasks],
  );

  useEffect(() => {
    let ignore = false;

    async function loadRoadmap() {
      setIsLoading(true);
      setError(null);

      try {
        const [tasksResponse, adminResponse] = await Promise.all([
          apiClient.get<RoadmapTask[]>("/questionnaire/tasks"),
          apiClient.get<{ can_edit_roadmap: boolean }>("/questionnaire/admin-status"),
        ]);
        if (!ignore) {
          setTasks(tasksResponse.data);
          setCanEditRoadmap(adminResponse.data.can_edit_roadmap);
        }
      } catch {
        if (!ignore) {
          setError("Не вдалося завантажити дорожню карту.");
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadRoadmap();

    return () => {
      ignore = true;
    };
  }, []);

  const openTask = (task: RoadmapTask) => {
    setSelectedTask(task);
    setDraft(toDraft(task));
    setIsEditing(false);
    setSaveError(null);
  };

  const closeTask = () => {
    setSelectedTask(null);
    setDraft(null);
    setIsEditing(false);
    setSaveError(null);
  };

  const saveTask = async () => {
    if (!selectedTask || !draft) {
      return;
    }

    setIsSaving(true);
    setSaveError(null);

    try {
      const response = await apiClient.put<RoadmapTask>(
        `/questionnaire/tasks/${selectedTask.id}`,
        {
          title: draft.title,
          description: draft.description,
          guidance: draft.guidance || null,
          references: draft.references || null,
          legal_basis: draft.legal_basis,
          deadline_days: Number(draft.deadline_days),
        },
      );

      setTasks((current) =>
        current.map((task) => (task.id === response.data.id ? response.data : task)),
      );
      setSelectedTask(response.data);
      setDraft(toDraft(response.data));
      setIsEditing(false);
    } catch {
      setSaveError("Не вдалося зберегти зміни. Перевірте права адміністратора.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Stack id="roadmap" spacing={3}>
      <Box>
        <Typography variant="h2" component="h2">
          Дорожня карта
        </Typography>
        <Typography color="text.secondary">
          {completedCount} з {tasks.length} завдань виконано.
        </Typography>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Stack spacing={2}>
          {tasks.length === 0 && (
            <Alert severity="info">
              Дорожня карта ще не сформована. Пройдіть опитувальник, щоб отримати перші завдання.
            </Alert>
          )}

          {tasks.map((task, index) => (
            <Box
              key={task.id}
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
                  {index + 1}
                </Box>
                <Box sx={{ width: 2, flexGrow: 1, bgcolor: "divider", mt: 1 }} />
              </Box>

              <Card variant="outlined" sx={{ borderRadius: 2 }}>
                <CardActionArea onClick={() => openTask(task)}>
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
                          label={statusLabels[task.status] ?? task.status}
                          color={task.status === "DONE" ? "success" : "info"}
                          variant={task.status === "PENDING" ? "outlined" : "filled"}
                          sx={{ alignSelf: { xs: "flex-start", sm: "center" } }}
                        />
                      </Box>

                      <Typography color="text.secondary">{task.description}</Typography>
                    </Stack>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Box>
          ))}
        </Stack>
      )}

      <TaskDialog
        canEdit={canEditRoadmap}
        draft={draft}
        isEditing={isEditing}
        isSaving={isSaving}
        onClose={closeTask}
        onDraftChange={setDraft}
        onEdit={() => setIsEditing(true)}
        onSave={saveTask}
        open={Boolean(selectedTask)}
        saveError={saveError}
        task={selectedTask}
      />
    </Stack>
  );
}

type TaskDialogProps = {
  canEdit: boolean;
  draft: RoadmapTaskDraft | null;
  isEditing: boolean;
  isSaving: boolean;
  onClose: () => void;
  onDraftChange: (draft: RoadmapTaskDraft) => void;
  onEdit: () => void;
  onSave: () => void;
  open: boolean;
  saveError: string | null;
  task: RoadmapTask | null;
};

function TaskDialog({
  canEdit,
  draft,
  isEditing,
  isSaving,
  onClose,
  onDraftChange,
  onEdit,
  onSave,
  open,
  saveError,
  task,
}: TaskDialogProps) {
  if (!task || !draft) {
    return null;
  }

  const updateDraft = (field: keyof RoadmapTaskDraft, value: string) => {
    onDraftChange({ ...draft, [field]: value });
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle sx={{ pr: 7 }}>
        {isEditing ? "Редагування кроку" : task.title}
        <IconButton
          aria-label="Закрити"
          onClick={onClose}
          sx={{ position: "absolute", right: 12, top: 12 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2.5}>
          {saveError && <Alert severity="error">{saveError}</Alert>}

          {isEditing ? (
            <>
              <TextField
                label="Назва кроку"
                value={draft.title}
                onChange={(event) => updateDraft("title", event.target.value)}
                fullWidth
              />
              <TextField
                label="Опис"
                value={draft.description}
                onChange={(event) => updateDraft("description", event.target.value)}
                fullWidth
                multiline
                minRows={3}
              />
              <TextField
                label="Підказки для виконання"
                value={draft.guidance}
                onChange={(event) => updateDraft("guidance", event.target.value)}
                fullWidth
                multiline
                minRows={4}
              />
              <TextField
                label="Референси"
                value={draft.references}
                onChange={(event) => updateDraft("references", event.target.value)}
                fullWidth
                multiline
                minRows={3}
              />
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", sm: "1fr 180px" },
                  gap: 2,
                }}
              >
                <TextField
                  label="Правова основа"
                  value={draft.legal_basis}
                  onChange={(event) => updateDraft("legal_basis", event.target.value)}
                  fullWidth
                />
                <TextField
                  label="Строк, днів"
                  type="number"
                  value={draft.deadline_days}
                  onChange={(event) => updateDraft("deadline_days", event.target.value)}
                  fullWidth
                  slotProps={{ htmlInput: { min: 1 } }}
                />
              </Box>
            </>
          ) : (
            <>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Правова основа
                </Typography>
                <Typography>{task.legal_basis}</Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Строк виконання
                </Typography>
                <Typography>{task.deadline_days} днів</Typography>
              </Box>
              <Box>
                <Typography variant="h3" component="h3">
                  Опис
                </Typography>
                <Typography sx={{ mt: 1 }} color="text.secondary">
                  {task.description}
                </Typography>
              </Box>
              <Box>
                <Typography variant="h3" component="h3">
                  Підказки
                </Typography>
                <Typography sx={{ mt: 1 }} color="text.secondary">
                  {task.guidance || "Підказки для цього кроку ще не додані."}
                </Typography>
              </Box>
              <Box>
                <Typography variant="h3" component="h3">
                  Референси
                </Typography>
                <Typography sx={{ mt: 1 }} color="text.secondary">
                  {task.references || "Референси для цього кроку ще не додані."}
                </Typography>
              </Box>
            </>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        {canEdit && !isEditing && (
          <Button startIcon={<EditIcon />} onClick={onEdit}>
            Редагувати
          </Button>
        )}
        {isEditing && (
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={isSaving || !draft.title || !draft.description || !draft.legal_basis}
            onClick={onSave}
          >
            {isSaving ? "Збереження..." : "Зберегти"}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}

function toDraft(task: RoadmapTask): RoadmapTaskDraft {
  return {
    title: task.title,
    description: task.description,
    guidance: task.guidance ?? "",
    references: task.references ?? "",
    legal_basis: task.legal_basis,
    deadline_days: String(task.deadline_days),
  };
}
