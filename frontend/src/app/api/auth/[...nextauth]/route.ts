// frontend/src/app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import authOptions from "@/lib/auth/options";

// cast to any to avoid type incompatibilities between packages
const handler = (NextAuth as any)(authOptions as any);

export { handler as GET, handler as POST };
