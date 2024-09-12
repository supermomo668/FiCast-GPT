export const LANDING_CHARACTERS = [
  {
    name: "Joe Rogan",
    description: "Joe Rogan is a comedian, UFC commentator, and host of 'The Joe Rogan Experience'",
    image: "https://i.ibb.co/m9ywqcs/Joe-Rogan.png",
    model: null, // Handled by backend
    role: "host",
  },
  {
    name: "Harry Potter",
    description: "The boy who lived, a wizard from the world of Harry Potter",
    image:
      "https://replicate.delivery/pbxt/QjGtucx4kAKBPxi4UwAOTTVteSJmezbq40k7NDwo5w16jjDTA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Iron Man",
    description: "Tony Stark, a billionaire inventor in a powered suit",
    image:
      "https://replicate.delivery/pbxt/t2T7oFjCUcbgOpFplfckt3Tb7fOvQ0f88clfEwPXNOMvyUOMB/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Darth Vader",
    description: "The Sith Lord from Star Wars",
    image:
      "https://replicate.delivery/pbxt/CEBtzXHIOT7VDtPHeBXwAJDlcwcZ4cM42tuJ4A7zTMP1zxhJA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Alan Turing",
    description: "A pioneering computer scientist and mathematician",
    image:
      "https://replicate.delivery/pbxt/eboohJoDnOTvJ62MOZzsVnNJJDyOAe1cp4mYwlcQ2nxHPlDTA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Albert Einstein",
    description: "Theoretical physicist known for the theory of relativity",
    image:
      "https://replicate.delivery/pbxt/BtneAyluBHUPHqZ9NFauyH5P65Fkwuf3LbvAUjfZ0be9HVOMB/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Genghis Khan",
    description: "Founder and first Great Khan of the Mongol Empire",
    image:
      "https://replicate.delivery/pbxt/ZtJM15tz4n6nGpZkZ2bi6yLTfi4MGE3emyLHAUXir1JoUlDTA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Elon Musk",
    description: "Entrepreneur and CEO of SpaceX and Tesla",
    image:
      "https://replicate.delivery/pbxt/zxT3wXAdPE6rNJP1sfroJiTawHskstDIJyX2ufD4fXaw8LHmA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Jensen Huang",
    description: "Entrepreneur and CEO of Nvidia",
    image: "https://i.ibb.co/4Mw6Htt/Jensen-Huang.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Gordon Ramsay",
    description: "Celebrity chef known for his fiery temperament",
    image:
      "https://replicate.delivery/pbxt/eN4pHz2D49XAYqPxnaFcZolYxGzEcdlmpBk5cen8Ib7fFMHmA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "George Costanza",
    description: "A fictional character from the TV show 'Seinfeld'",
    image:
      "https://replicate.delivery/pbxt/ee6pd1uxwrkaGE30ZYlUnIkREUkyn1bNvcTz7VvmRLf2JMHmA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Donald Trump",
    description: "45th President of the United States and businessman",
    image:
      "https://replicate.delivery/pbxt/EwtmumDFmBoxMB6vF207UslR2vZmHoLUPnWffBkizfGXYPHmA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Joe Biden",
    description: "46th President of the United States",
    image:
      "https://replicate.delivery/pbxt/95cRhihedm1dACCau0LKI0dPSreCLd9qwpSbosiJhC1eaPHmA/ComfyUI_00002_.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Angela Markel",
    description: "Retired German politician who served as Chancellor of Germany from 2005 to 2021 and was the first woman to hold that office",
    image: "https://i.ibb.co/qymPbXp/Angela-Markel.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Megan Jovon Ruth Pete (Megan Thee Stallion)",
    description: "known professionally as Megan Thee Stallion, is an American rapper, singer, and songwriter",
    image: "https://i.ibb.co/wJR6HTJ/Megan-Thee-Stallion.png",
    model: null, // Handled by backend
    role: "guest",
  },
  {
    name: "Andrew Huberman",
    description: "Neuroscientist and professor at Stanford University",
    image: "https://i.ibb.co/HFZ6VvW/Andrew-Huberman.png",
    model: null, // Handled by backend
    role: "host",
  },
  {
    name: "Neil deGrasse Tyson",
    description: "Astrophysicist and science communicator",
    image: "https://i.ibb.co/p0mydmw/Neil-Tyson.png",
    model: null, // Handled by backend
    role: "guest",
  },
  
];

export const CharacterImages = new Map(
  LANDING_CHARACTERS.map((ch) => [ch.name, ch.image])
);

const BlankAvatarImage = "https://www.shutterstock.com/image-vector/user-profile-icon-vector-avatar-600nw-2220431045.jpg";

export const CUSTOM = {
  name: "Custom",
  description: "Custom character",
  image: BlankAvatarImage,
  model: null,
  role: "guest",
};