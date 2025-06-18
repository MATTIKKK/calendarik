FROM node:22

WORKDIR /app

COPY . .

RUN npm install
RUN npm run build

# Optional: serve with static server
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "5173"]
#CMD ["npm", "run", "dev"]