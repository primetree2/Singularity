import Link from "next/link";

type Props = {
  statusCode?: number;
};

export default function Error({ statusCode }: Props) {
  let message = "An error occurred";

  if (statusCode === 404) message = "Page not found";
  else if (statusCode === 500) message = "Server error";

  return (
    <div className="h-screen flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-5xl font-bold mb-4">{statusCode || ""}</h1>
      <p className="text-xl text-gray-600 mb-6">{message}</p>
      <Link
        href="/"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Go Back Home
      </Link>
    </div>
  );
}

Error.getInitialProps = ({ res, err }: any) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
  return { statusCode };
};
