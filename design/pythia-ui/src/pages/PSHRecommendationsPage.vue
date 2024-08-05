<i18n>
en:
  main_title: PSH topics recommendations

cs:
  main_title: Doporučená PSH témata
</i18n>

<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h2>{{ $t("main_title") }}</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-0">
        <ExplicitTopicRecommendationsWidget topic-type="psh" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ExplicitTopicRecommendationsWidget from "../components/ExplicitTopicRecommendationsWidget";

export default {
  name: "AuthorRecommendationsPage",
  components: { ExplicitTopicRecommendationsWidget },
};
</script>
