import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import ArticleIcon from "@mui/icons-material/Article";
import DashboardIcon from "@mui/icons-material/Dashboard";
import FactCheckIcon from "@mui/icons-material/FactCheck";
import MenuIcon from "@mui/icons-material/Menu";
import RouteIcon from "@mui/icons-material/Route";
import StorageIcon from "@mui/icons-material/Storage";
import {
  AppBar,
  Box,
  Button,
  Chip,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { ReactNode, useState } from "react";

const drawerWidth = 280;

const navItems = [
  { label: "Кабінет", icon: <DashboardIcon />, href: "#dashboard" },
  { label: "Дорожня карта", icon: <RouteIcon />, href: "#roadmap" },
  { label: "НПА", icon: <ArticleIcon />, href: "#legal-acts" },
  { label: "Реєстр систем", icon: <StorageIcon />, href: "#systems" },
];

type LayoutProps = {
  children: ReactNode;
  onLogout?: () => void;
  user?: {
    email: string;
    is_admin: boolean;
  } | null;
};

export function Layout({ children, onLogout, user }: LayoutProps) {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const [mobileOpen, setMobileOpen] = useState(false);

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Toolbar sx={{ minHeight: 72, px: 3 }}>
        <Box>
          <Typography variant="h3" component="div" sx={{ color: "primary.main" }}>
            CyberLaw Navigator
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Кабінет відповідності
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1.5, py: 2 }}>
        {navItems.map((item, index) => (
          <ListItemButton
            key={item.label}
            component="a"
            href={item.href}
            selected={index === 0}
            sx={{
              minHeight: 48,
              borderRadius: 1,
              mb: 0.5,
              "&.Mui-selected": {
                bgcolor: "rgba(18, 53, 91, 0.1)",
                color: "primary.main",
              },
              "&.Mui-selected .MuiListItemIcon-root": {
                color: "primary.main",
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40, color: "text.secondary" }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.label}
              slotProps={{ primary: { sx: { fontWeight: 700 } } }}
            />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar
        position="fixed"
        color="inherit"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ minHeight: 72, gap: 2 }}>
          {!isDesktop && (
            <IconButton
              color="primary"
              edge="start"
              aria-label="Відкрити навігацію"
              onClick={() => setMobileOpen(true)}
            >
              <MenuIcon />
            </IconButton>
          )}
          <FactCheckIcon color="primary" />
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="h3" component="h1" noWrap>
              Кабінет кіберкомплаєнсу
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              Оцінка, дорожня карта та документи відповідності
            </Typography>
          </Box>
          {user && (
            <Chip
              icon={<AccountCircleIcon />}
              label={user.is_admin ? "Адміністратор" : "Користувач"}
              color={user.is_admin ? "primary" : "default"}
              variant={user.is_admin ? "filled" : "outlined"}
              sx={{ display: { xs: "none", sm: "inline-flex" } }}
            />
          )}
          {onLogout && (
            <Button variant="outlined" color="secondary" onClick={onLogout}>
              Вийти
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="Основна навігація"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          ml: { md: `${drawerWidth}px` },
          pt: "72px",
          minHeight: "100vh",
        }}
      >
        <Box sx={{ px: { xs: 2, sm: 3, lg: 4 }, py: 3 }}>{children}</Box>
      </Box>
    </Box>
  );
}
