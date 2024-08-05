<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
    works: Works
    go_there: Show page
    functions: Functions
    additional_functions: Additional functions
cs:
    works: Díla
    go_there: Zobrazit stránku
    functions: Funkce
    additional_functions: Doplňkové funkce
</i18n>

<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h1>Pythia</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-alert type="info" outlined>
          <p>
            <b>TIP</b>: V horním menu můžete kliknutím na
            <span class="sc">Rozmezí dat</span> nastavit období za které bude
            započítáván zájem o díla v jednotlivých pohledech na data.
          </p>
          <p>
            Pomocí voleb v položce <span class="sc">Filtr děl</span> můžete dále
            ovlivnit, jaká díla budou brána při doporučeních v potaz. Můžete tak
            filtrovat např. podle jazyka díla, roku vydání, atp.
          </p>
        </v-alert>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <h2 v-text="$t('functions')"></h2>
      </v-col>
    </v-row>

    <v-row>
      <v-col
        :cols="12"
        :md="6"
        :lg="4"
        v-for="item in items"
        :key="item.linkName"
      >
        <v-card class="fill-height">
          <v-card-title primary-title>
            <router-link :to="{ name: item.linkName }" class="headline">{{
              item.linkText
            }}</router-link>
          </v-card-title>
          <v-card-text>
            {{ item.desc }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <h2 v-text="$t('additional_functions')"></h2>
      </v-col>
    </v-row>

    <v-row>
      <v-col
        :cols="12"
        :md="6"
        :lg="4"
        v-for="item in extraItems"
        :key="item.linkName"
      >
        <v-card class="fill-height">
          <v-card-title primary-title>
            <router-link :to="{ name: item.linkName }" class="headline">{{
              item.linkText
            }}</router-link>
          </v-card-title>
          <v-card-text>
            {{ item.desc }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "HomePage",

  data() {
    return {
      items: [
        {
          linkName: "psh recommendations",
          linkText: "Doporučená témata",
          desc: `poskytuje detailní přehled o tom, která témata (podle PSH - polytématického strukturovaného
                    hesláře) jsou nejvíce poptávána. Možnost porovnávat u témat jejich zastoupení ve
                    fondu se zájmem o ně umožňuje vytipovat témata, na která by bylo vhodné se zaměřit
                    v akvizici. Jako doplňkové informace je možno ke každému tématu zobrazit seznam
                    vydavatelů a autorů, kteří jsou pro toto téma nejvíce půjčovaní a získat tak detailnější
                    tip k akvizici.`,
        },
        {
          linkName: "publisher recommendations",
          linkText: "Doporučení vydavatelé",
          desc: `poskytuje přehled díla kterých vydavatelů se nejvíce půjčují. To umožňuje vytipovat
                na které vydavatele se zaměřit pro výběr nových akvizic. Podobně jako u témat je možné
                získat přehled souvisejících autorů, témat, atd.`,
        },
        {
          linkName: "author recommendations",
          linkText: "Doporučení autoři",
          desc: `poskytuje přehled nejvíce půjčovaných autorů. To umožňuje zaměřit akvizici na autory,
                u kterých již bylo prokázáno, že je o jejich tvorbu zájem a je tedy pravděpodobné,
                že i jejich nová díla budou půjčovaná. Stejně jako u ostatních doporučení je možné
                pro každého autora získat přehled jazyků, vydavatelů a témat, která s ním souvisejí.`,
        },
      ],
      extraItems: [
        {
          linkName: "work detail root",
          linkText: "Detail díla",
          desc: `umožňuje vyhledávat v obsahu fondu a zobrazit si bibliografické údaje
                a informace o půjčovanosti konkrétního titulu.`,
        },
      ],
    };
  },

  methods: {
    reloadWorksets() {
      this.$store.dispatch("loadWorksets");
    },
  },
};
</script>

<style scoped></style>
