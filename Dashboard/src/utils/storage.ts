const TOKEN_KEY = 'rdcms.jwt';
const USER_KEY = 'rdcms.user';

export const storage = {
  getToken: () => sessionStorage.getItem(TOKEN_KEY),
  setToken: (token: string) => sessionStorage.setItem(TOKEN_KEY, token),
  clearToken: () => sessionStorage.removeItem(TOKEN_KEY),
  getUser: () => {
    const raw = sessionStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) as unknown : null;
  },
  setUser: (user: unknown) => sessionStorage.setItem(USER_KEY, JSON.stringify(user)),
  clearUser: () => sessionStorage.removeItem(USER_KEY)
};
