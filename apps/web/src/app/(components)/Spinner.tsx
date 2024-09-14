import React from "react";

export const Spinner = () => {
  return (
    <div className="flex justify-center items-center">
      <div className="w-16 h-16 border-4 border-purple-500 border-solid border-t-transparent rounded-full animate-spin"></div>
    </div>
  );
};

export default Spinner;
