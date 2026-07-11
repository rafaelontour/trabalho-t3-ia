import type { Metadata } from "next";

import "@/app/globals.css";

export const metadata: Metadata = {
  title: "Recomenda Livros",
  description: "Recomendação semântica de livros"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
