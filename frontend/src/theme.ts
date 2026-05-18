import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#12355B",
      light: "#2F5C86",
      dark: "#0A223A",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#6F879D",
      light: "#A6B6C4",
      dark: "#435B70",
      contrastText: "#FFFFFF",
    },
    background: {
      default: "#F4F6F8",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#162331",
      secondary: "#52616F",
    },
    divider: "#D7DEE6",
    error: {
      main: "#B42318",
    },
    warning: {
      main: "#A15C07",
    },
    success: {
      main: "#1E6B4E",
    },
    info: {
      main: "#286489",
    },
  },
  typography: {
    fontFamily:
      '"Inter", "Roboto", "Segoe UI", "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontSize: "2rem",
      fontWeight: 700,
      letterSpacing: 0,
    },
    h2: {
      fontSize: "1.5rem",
      fontWeight: 700,
      letterSpacing: 0,
    },
    h3: {
      fontSize: "1.25rem",
      fontWeight: 700,
      letterSpacing: 0,
    },
    body1: {
      lineHeight: 1.6,
    },
    button: {
      fontWeight: 700,
      letterSpacing: 0,
      textTransform: "none",
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: "#A6B6C4 #F4F6F8",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          boxShadow: "none",
        },
      },
      defaultProps: {
        disableElevation: true,
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: "none",
          borderBottom: "1px solid #D7DEE6",
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: "1px solid #D7DEE6",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
  },
});
