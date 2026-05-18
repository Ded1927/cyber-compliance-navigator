import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import BusinessIcon from "@mui/icons-material/Business";
import SecurityIcon from "@mui/icons-material/Security";
import axios from "axios";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from "@mui/material";
import { Dispatch, SetStateAction, useMemo, useState } from "react";

import { apiClient } from "../../api/client";

type QuestionnaireState = {
  orgType: string;
  hasDir: boolean;
  hasIzod: boolean;
  isOki: boolean;
  isOkii: boolean;
  criticalityCategory: "I" | "II" | "III" | "IV" | "";
};

const initialState: QuestionnaireState = {
  orgType: "",
  hasDir: false,
  hasIzod: false,
  isOki: false,
  isOkii: false,
  criticalityCategory: "",
};

const steps = ["Профіль", "Інформація", "Критичність", "Підтвердження"];

const orgTypes = [
  { value: "state_body", label: "Орган державної влади" },
  { value: "local_gov", label: "Орган місцевого самоврядування" },
  { value: "state_enterprise", label: "Державне підприємство" },
  { value: "private", label: "Приватна компанія" },
];

type AnonymousTask = {
  index: number;
  title: string;
  description: string;
  guidance: string | null;
  references: string | null;
  legal_basis: string;
  deadline_days: number;
};

type QuestionnaireFeatureProps = {
  /** Callback for authenticated mode. */
  onComplete?: () => void;
  /** If true, the questionnaire calls the anonymous endpoint and does not require auth. */
  anonymous?: boolean;
  /** Callback for anonymous mode — receives generated tasks and org type key. */
  onAnonymousComplete?: (tasks: AnonymousTask[], orgType: string) => void;
  /** Navigate to the login screen (shown in anonymous mode). */
  onGoToLogin?: () => void;
};

export function QuestionnaireFeature({
  onComplete,
  anonymous,
  onAnonymousComplete,
  onGoToLogin,
}: QuestionnaireFeatureProps) {
  const [activeStep, setActiveStep] = useState(0);
  const [answers, setAnswers] = useState<QuestionnaireState>(initialState);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);

  const canGoNext = useMemo(() => {
    if (activeStep === 0) {
      return Boolean(answers.orgType);
    }

    if (activeStep === 2 && (answers.isOki || answers.isOkii)) {
      return Boolean(answers.criticalityCategory);
    }

    return true;
  }, [activeStep, answers.criticalityCategory, answers.isOki, answers.isOkii, answers.orgType]);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    const payload = {
      org_type: answers.orgType,
      is_oki_or_okii: answers.isOki || answers.isOkii,
      category: answers.isOki || answers.isOkii ? answers.criticalityCategory : null,
      data_type: getDataType(answers),
    };

    try {
      if (anonymous) {
        // Anonymous flow: call the unauthenticated endpoint
        const response = await apiClient.post<AnonymousTask[]>(
          "/questionnaire/anonymous-submit",
          payload,
        );
        onAnonymousComplete?.(response.data, answers.orgType);
      } else {
        // Authenticated flow
        await apiClient.post("/questionnaire/submit", payload);
        setIsCompleted(true);
        onComplete?.();
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        const message = typeof detail === "string" ? detail : error.message;
        setSubmitError(`Не вдалося сформувати дорожню карту: ${message}`);
      } else {
        setSubmitError("Не вдалося сформувати дорожню карту. Спробуйте ще раз.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 }, borderRadius: 2 }}>
      <Stack spacing={3}>
        <Box>
          <Typography variant="h2" component="h2">
            Опитувальник
          </Typography>
          <Typography color="text.secondary">
            Визначте первинний профіль організації для генерації дорожньої карти.
          </Typography>
        </Box>

        <Stepper activeStep={activeStep} alternativeLabel sx={{ display: { xs: "none", sm: "flex" } }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {isCompleted && (
          <Alert severity="success">
            Відповіді збережено. Дорожня карта буде оновлена за результатами опитування.
          </Alert>
        )}
        {submitError && <Alert severity="error">{submitError}</Alert>}

        <Box sx={{ minHeight: 220 }}>{renderStepContent(activeStep, answers, setAnswers)}</Box>

        <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2, flexWrap: "wrap" }}>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              disabled={activeStep === 0 || isSubmitting}
              onClick={() => setActiveStep((step) => Math.max(step - 1, 0))}
            >
              Назад
            </Button>
            {anonymous && onGoToLogin && (
              <Button variant="text" color="secondary" onClick={onGoToLogin}>
                Увійти замість цього
              </Button>
            )}
          </Box>
          {activeStep === steps.length - 1 ? (
            <Button
              variant="contained"
              startIcon={<AssignmentTurnedInIcon />}
              disabled={!canGoNext || isSubmitting}
              onClick={handleSubmit}
            >
              {isSubmitting ? "Формування..." : "Сформувати дорожню карту"}
            </Button>
          ) : (
            <Button
              variant="contained"
              disabled={!canGoNext}
              onClick={() => setActiveStep((step) => step + 1)}
            >
              Далі
            </Button>
          )}
        </Box>
      </Stack>
    </Paper>
  );
}

function renderStepContent(
  activeStep: number,
  answers: QuestionnaireState,
  setAnswers: Dispatch<SetStateAction<QuestionnaireState>>,
) {
  if (activeStep === 0) {
    return (
      <Stack spacing={2.5}>
        <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
          <BusinessIcon color="primary" />
          <Typography variant="h3">Форма власності та тип організації</Typography>
        </Stack>
        <FormControl fullWidth>
          <InputLabel id="org-type-label">Тип організації</InputLabel>
          <Select
            labelId="org-type-label"
            label="Тип організації"
            value={answers.orgType}
            onChange={(event) =>
              setAnswers((current) => ({ ...current, orgType: event.target.value }))
            }
          >
            {orgTypes.map((type) => (
              <MenuItem key={type.value} value={type.value}>
                {type.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Stack>
    );
  }

  if (activeStep === 1) {
    return (
      <Stack spacing={2.5}>
        <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
          <SecurityIcon color="primary" />
          <Typography variant="h3">ДІР та інформація з обмеженим доступом</Typography>
        </Stack>
        <FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                checked={answers.hasDir}
                onChange={(event) =>
                  setAnswers((current) => ({
                    ...current,
                    hasDir: event.target.checked,
                  }))
                }
              />
            }
            label="Організація обробляє державні інформаційні ресурси"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={answers.hasIzod}
                onChange={(event) =>
                  setAnswers((current) => ({
                    ...current,
                    hasIzod: event.target.checked,
                  }))
                }
              />
            }
            label="Організація обробляє інформацію з обмеженим доступом"
          />
        </FormGroup>
      </Stack>
    );
  }

  if (activeStep === 2) {
    return (
      <Stack spacing={2.5}>
        <Typography variant="h3">ОКІ / ОКІІ</Typography>
        <FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                checked={answers.isOki}
                onChange={(event) =>
                  setAnswers((current) => ({
                    ...current,
                    isOki: event.target.checked,
                    criticalityCategory:
                      event.target.checked || current.isOkii ? current.criticalityCategory : "",
                  }))
                }
              />
            }
            label="Організація належить до об'єктів критичної інфраструктури"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={answers.isOkii}
                onChange={(event) =>
                  setAnswers((current) => ({
                    ...current,
                    isOkii: event.target.checked,
                    criticalityCategory:
                      event.target.checked || current.isOki ? current.criticalityCategory : "",
                  }))
                }
              />
            }
            label="Є системи або сервіси з ознаками ОКІІ"
          />
        </FormGroup>
        {(answers.isOki || answers.isOkii) && (
          <FormControl fullWidth>
            <InputLabel id="criticality-category-label">Категорія критичності</InputLabel>
            <Select
              labelId="criticality-category-label"
              label="Категорія критичності"
              value={answers.criticalityCategory}
              onChange={(event) =>
                setAnswers((current) => ({
                  ...current,
                  criticalityCategory: event.target.value as "I" | "II" | "III" | "IV",
                }))
              }
            >
              {["I", "II", "III", "IV"].map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      </Stack>
    );
  }

  return (
    <Stack spacing={1.5}>
      <Typography variant="h3">Підтвердження відповідей</Typography>
      <Typography color="text.secondary">
        Тип організації: {orgTypes.find((type) => type.value === answers.orgType)?.label}
      </Typography>
      <Typography color="text.secondary">
        ДІР: {answers.hasDir ? "так" : "ні"}; ІзОД: {answers.hasIzod ? "так" : "ні"}
      </Typography>
      <Typography color="text.secondary">
        ОКІ: {answers.isOki ? "так" : "ні"}; ОКІІ: {answers.isOkii ? "так" : "ні"}
      </Typography>
      {(answers.isOki || answers.isOkii) && (
        <Typography color="text.secondary">
          Категорія критичності: {answers.criticalityCategory}
        </Typography>
      )}
    </Stack>
  );
}

function getDataType(answers: QuestionnaireState) {
  if (answers.hasDir && answers.hasIzod) {
    return "dir_izod";
  }

  if (answers.hasDir) {
    return "dir";
  }

  if (answers.hasIzod) {
    return "izod";
  }

  return "none";
}
